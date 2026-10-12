"""Article 4: exploratory ABM of founder/customer network transformation.

All behavioral values are explicit, uncalibrated modeling assumptions.
Only NumPy is required to simulate. See METODOLOGIA.md before interpretation.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
import hashlib
import math
import numpy as np

VERSION = '0.1.0'
STRATEGIES = {
    'A': ('Contactos personales', (.70, .20, .05, .05)),
    'B': ('Exploración externa', (.20, .10, .10, .60)),
    'C': ('Referidos', (.35, .15, .40, .10)),
    'D': ('Equilibrada', (.30, .20, .30, .20)),
}
CHANNELS = {0: 'none', 1: 'direct', 2: 'exploration', 3: 'requested_referral', 4: 'spontaneous_wom'}

@dataclass(frozen=True)
class Config:
    population: int = 500
    communities: int = 5
    initial_contacts: int = 50
    initial_communities: int = 3
    months: int = 60
    founder_hours: float = 40.0
    p_within: float = .06
    p_between: float = .004
    sale_hours: float = 1.0
    maintenance_hours: float = .5
    referral_hours: float = 1.0
    exploration_hours: float = 2.0
    exploration_success: float = .65
    requested_success: float = .75
    spontaneous_rate: float = .30
    initial_tie_min: float = .60
    initial_tie_max: float = .90
    exploration_trust: float = .25
    referral_trust_advantage: float = .30
    maintenance_reinforcement: float = .15
    contact_reinforcement: float = .08
    tie_decay: float = .025
    tie_threshold: float = .05
    energy_decay: float = .08
    maintenance_energy: float = .08
    repeat_energy: float = .25
    product_quality: float = .85
    satisfaction_noise: float = .10
    promoter_threshold: float = .72
    dissatisfied_threshold: float = .45
    purchase_scale: float = 1.0
    trust_base: float = .25
    trust_weight: float = .60
    social_weight: float = .40
    social_influence: float = .50
    fatigue_penalty: float = .16
    negative_wom_penalty: float = .35
    repurchase_rate: float = .10
    active_months: int = 9
    capacity: int = 30
    congestion_penalty: float = .10
    autonomy_share: float = .50
    autonomy_external: float = .50
    autonomy_dependency: float = .50
    autonomy_communities: int = 3
    autonomy_months: int = 6
    founder_stop_month: int = 0

    def validate(self):
        assert 0 < self.initial_contacts <= self.population
        assert 1 <= self.initial_communities <= self.communities <= self.population
        assert self.initial_contacts <= sum(len(g) for g in np.array_split(np.arange(self.population), self.communities)[:self.initial_communities])
        assert self.months > 0 and self.capacity >= 0 and self.active_months > 0
        assert self.founder_hours >= 0 and self.autonomy_months > 0
        assert 0 <= self.autonomy_communities <= self.communities
        for k in ('p_within','p_between','exploration_success','requested_success','spontaneous_rate',
                  'social_influence','product_quality','repurchase_rate','tie_decay','energy_decay',
                  'promoter_threshold','dissatisfied_threshold','autonomy_share','autonomy_external','autonomy_dependency'):
            assert 0 <= getattr(self,k) <= 1, k
        assert all(getattr(self,k)>0 for k in ('sale_hours','maintenance_hours','referral_hours','exploration_hours'))
        assert self.initial_tie_min <= self.initial_tie_max <= 1

def rng_for(seed: int, month: int, stream: int):
    """Named streams preserve common person-month shocks across strategies."""
    return np.random.default_rng(np.random.SeedSequence([int(seed), int(month), int(stream)]))

@dataclass
class InitialState:
    community: np.ndarray
    social: np.ndarray
    social_strength: np.ndarray
    need: np.ndarray
    fit: np.ndarray
    initial: np.ndarray
    founder_strength: np.ndarray
    fingerprint: str

def make_initial(c: Config, seed: int) -> InitialState:
    c.validate()
    n=c.population
    groups=np.array_split(np.arange(n),c.communities)
    community=np.empty(n,dtype=int)
    for k,g in enumerate(groups): community[g]=k
    rg=rng_for(seed,0,1)
    u=rg.random((n,n)); p=np.where(community[:,None]==community[None,:],c.p_within,c.p_between)
    social=np.triu(u<p,1); social=social|social.T
    # A ring within each community ensures within-community connectivity only.
    for g in groups:
        if len(g)>1:
            social[g,np.roll(g,-1)]=True; social[np.roll(g,-1),g]=True
    np.fill_diagonal(social,False)
    w=np.triu(rg.uniform(.4,.9,(n,n)),1); w=w+w.T
    w=np.where(social,w,0.)
    need=rg.beta(2,2,n); fit=rg.beta(2,2,n)
    eligible=np.concatenate(groups[:c.initial_communities])
    initial=np.zeros(n,dtype=bool); initial[rg.choice(eligible,c.initial_contacts,replace=False)]=True
    founder=np.zeros(n); founder[initial]=rg.uniform(c.initial_tie_min,c.initial_tie_max,initial.sum())
    digest=hashlib.sha256()
    for arr in (community,social,need,fit,initial,founder): digest.update(arr.tobytes())
    return InitialState(community,social,w,need,fit,initial,founder,digest.hexdigest()[:16])

def ratio(a,b):
    return float(a/b) if b else float('nan')

def autonomy_criteria(row: dict, c: Config) -> bool:
    return bool(row['new_customers']>0 and row['autonomous_share']>c.autonomy_share
        and row['external_share']>c.autonomy_external and row['net_active_growth']>0
        and row['founder_sales_share']<c.autonomy_dependency
        and row['communities_reached']>=c.autonomy_communities)

class Model:
    def __init__(self,c: Config,seed:int,strategy:str,trace=False,initial:InitialState|None=None):
        c.validate(); assert strategy in STRATEGIES
        self.c=c; self.seed=seed; self.strategy=strategy; self.trace=trace
        self.init=initial if initial is not None else make_initial(c,seed)
        n=c.population
        self.founder=self.init.founder_strength.copy()
        self.bought=np.zeros(n,bool); self.first_month=np.zeros(n,int)
        self.last_purchase=np.full(n,-1000,int); self.satisfaction=np.zeros(n); self.energy=np.zeros(n)
        self.contact_count=np.zeros(n,int); self.approached_initial=np.zeros(n,bool)
        self.origin=np.zeros(n,int); self.origin_referrer=np.full(n,-1,int)
        self.origin_month=np.zeros(n,int); self.founder_ever=np.zeros(n,bool)
        self.acquisition_founder=np.zeros(n,bool); self.acquisition_autonomous=np.zeros(n,bool)
        self.acquisition_bridge=np.zeros(n,bool)
        self.referral_links={}; self.link_events=[]; self.exposure_events=[]; self.sales=[]
        self.periods=[]; self.snapshots=[]; self.streak=0; self.first_autonomy=0; self.autonomy_periods=0
        self.previous_active=0; self.cumulative_sales=0; self.cumulative_autonomous=0
        self.degree=self.init.social.sum(axis=1)
        self.neighbors=[np.flatnonzero(self.init.social[i]) for i in range(n)]
        if trace:self.snapshot(0)

    def log_link(self,month,source,target,layer,event,strength,mechanism):
        if self.trace:self.link_events.append(dict(seed=self.seed,strategy=self.strategy,month=month,
            source=int(source),target=int(target),layer=layer,event=event,strength=float(strength),mechanism=mechanism))

    def update_founder_tie(self,i,value,month,mechanism):
        old=self.founder[i]; self.founder[i]=min(1.,value)
        if old==0 and value>0:self.log_link(month,-1,i,'founder','created',self.founder[i],mechanism)
        elif self.trace:self.log_link(month,-1,i,'founder','reinforced',self.founder[i],mechanism)

    def snapshot(self,month):
        active=self.bought & ((month-self.last_purchase)<self.c.active_months)
        self.snapshots.append(dict(month=month,founder=self.founder.copy(),bought=self.bought.copy(),
            active=active.copy(),energy=self.energy.copy(),satisfaction=self.satisfaction.copy(),
            referral_links=dict(self.referral_links)))

    def step(self,month):
        c=self.c; n=c.population; S=self.init
        active_start=self.bought & ((month-self.last_purchase)<c.active_months)
        promoter=active_start & (self.satisfaction>=c.promoter_threshold) & (self.energy>0)
        interacted=np.zeros(n,bool); commercial_interactions=set(); exposures=[]
        hours=c.founder_hours if not(c.founder_stop_month and month>=c.founder_stop_month) else 0.
        allocation=np.array(STRATEGIES[self.strategy][1])*hours
        spent=np.zeros(4); used=np.zeros(4,int)
        action_costs=np.array([c.sale_hours,c.maintenance_hours,c.referral_hours,c.exploration_hours])
        slots=np.floor((allocation+1e-10)/action_costs).astype(int)
        priority=rng_for(self.seed,month,10).random(n)

        def expose(target,channel,referrer,trust):
            exposures.append((int(target),int(channel),int(referrer),float(trust)))
            if channel in (1,2,3):self.founder_ever[target]=True
            if S.initial[target]:self.approached_initial[target]=True
            if channel in (3,4):
                key=(int(referrer),int(target)); old=self.referral_links.get(key,0.)
                self.referral_links[key]=min(1.,max(old,trust)+c.contact_reinforcement)
                commercial_interactions.add(key)
                self.log_link(month,*key,'referral','created' if old==0 else 'reinforced',self.referral_links[key],CHANNELS[channel])

        # Selling only targets people who have not yet bought.
        eligible=(self.founder>0)&~self.bought
        if self.strategy=='A':eligible &= S.initial
        for i in np.flatnonzero(eligible)[np.argsort(priority[eligible])][:slots[0]]:
            used[0]+=1; interacted[i]=True
            self.update_founder_tie(i,self.founder[i]+c.contact_reinforcement,month,'direct')
            expose(i,1,-1,self.founder[i])

        # Weakest extant direct ties first, with stable random tie-breaking.
        eligible=np.flatnonzero(self.founder>0)
        order=np.lexsort((priority[eligible],self.founder[eligible]))
        for i in eligible[order][:slots[1]]:
            used[1]+=1; interacted[i]=True
            self.update_founder_tie(i,self.founder[i]+c.maintenance_reinforcement,month,'maintenance')
            if promoter[i]:self.energy[i]=min(1.,self.energy[i]+c.maintenance_energy)

        # Requested referrals require a satisfied active customer reachable by the founder.
        eligible=np.flatnonzero(promoter & (self.founder>0))
        referral_u=rng_for(self.seed,month,20).random(n)
        target_u=rng_for(self.seed,month,21).random(n)
        for i in eligible[np.argsort(priority[eligible])][:slots[2]]:
            used[2]+=1; interacted[i]=True
            self.update_founder_tie(i,self.founder[i]+c.contact_reinforcement,month,'request')
            cand=self.neighbors[i][~self.bought[self.neighbors[i]]]
            if len(cand) and referral_u[i]<c.requested_success*self.satisfaction[i]*self.energy[i]:
                j=int(cand[min(len(cand)-1,int(target_u[i]*len(cand)))])
                trust=np.clip(c.exploration_trust+c.referral_trust_advantage*S.social_strength[i,j],0,1)
                self.update_founder_tie(j,max(self.founder[j],trust),month,'requested_referral')
                interacted[j]=True; expose(j,3,i,trust)

        # Exploration can reconnect a lost founder tie, but targets only noncustomers.
        eligible=np.flatnonzero((self.founder==0)&~self.bought)
        exploration_u=rng_for(self.seed,month,30).random(n)
        for i in eligible[np.argsort(priority[eligible])][:slots[3]]:
            used[3]+=1
            if exploration_u[i]<c.exploration_success:
                self.update_founder_tie(i,c.exploration_trust,month,'exploration')
                interacted[i]=True; expose(i,2,-1,c.exploration_trust)

        # Spontaneous WOM does not require a direct founder tie or founder time.
        wom_u=rng_for(self.seed,month,40).random(n); wom_target=rng_for(self.seed,month,41).random(n)
        for i in np.flatnonzero(promoter):
            if wom_u[i]>=c.spontaneous_rate*self.satisfaction[i]*self.energy[i]:continue
            cand=self.neighbors[i][~self.bought[self.neighbors[i]]]
            if not len(cand):continue
            j=int(cand[min(len(cand)-1,int(wom_target[i]*len(cand)))])
            trust=np.clip(c.exploration_trust+c.referral_trust_advantage*S.social_strength[i,j],0,1)
            expose(j,4,i,trust)

        # One purchase trial per prospect-month. Attribution: first exposure ever,
        # random tie-break among same-month exposures; founder involvement is cumulative.
        grouped={}
        for e in exposures:grouped.setdefault(e[0],[]).append(e)
        attribution_u=rng_for(self.seed,month,50).random(n)
        purchase_u=rng_for(self.seed,month,51).random(n)
        candidates=[]; prior_counts=self.contact_count.copy()
        negative=active_start&(self.satisfaction<c.dissatisfied_threshold)
        for i,entries in grouped.items():
            if self.origin[i]==0:
                e=entries[min(len(entries)-1,int(attribution_u[i]*len(entries)))]
                self.origin[i]=e[1]; self.origin_referrer[i]=e[2]; self.origin_month[i]=month
            self.contact_count[i]+=len(entries)
            trust=max(e[3] for e in entries)
            nb=self.neighbors[i]; influence=float(active_start[nb].mean()) if len(nb) else 0.
            neg=float(negative[nb].mean()) if len(nb) else 0.
            p=c.purchase_scale*S.need[i]*S.fit[i]*(c.trust_base+c.trust_weight*trust+c.social_weight*c.social_influence*influence)
            p*=math.exp(-c.fatigue_penalty*int(prior_counts[i]))
            p*=max(0.,1-c.negative_wom_penalty*c.social_influence*neg)
            p=float(np.clip(p,0,1))
            if purchase_u[i]<p:candidates.append((i,False))
            if self.trace:
                for _,channel,referrer,tr in entries:
                    self.exposure_events.append(dict(seed=self.seed,strategy=self.strategy,month=month,person_id=i,
                        channel=CHANNELS[channel],referrer=referrer,trust=tr,purchase_probability=p,
                        founder_involved_ever=int(self.founder_ever[i]),origin=CHANNELS[self.origin[i]]))

        # Repeat purchases are self-service and do not count as new customers.
        repeat_u=rng_for(self.seed,month,52).random(n)
        repeat_p=c.repurchase_rate*S.need*(.4+.6*self.satisfaction)
        for i in np.flatnonzero(self.bought & (repeat_u<repeat_p)):candidates.append((int(i),True))
        capacity_priority=rng_for(self.seed,month,53).random(n)
        candidates.sort(key=lambda x:capacity_priority[x[0]])
        accepted=candidates[:c.capacity]
        unmet=max(0,len(candidates)-c.capacity)
        congestion=c.congestion_penalty*ratio(unmet,max(1,len(candidates)))
        satisfaction_noise=rng_for(self.seed,month,54).normal(0,c.satisfaction_noise,n)
        new_ids=[]; repeat_count=0; auto_count=0; founder_new=0; bridge_count=0
        by_channel={k:0 for k in range(1,5)}
        for i,repeat in accepted:
            self.last_purchase[i]=month
            if repeat:
                repeat_count+=1; self.energy[i]=min(1.,self.energy[i]+c.repeat_energy)
                # This prototype keeps satisfaction fixed after the first purchase.
                origin='repurchase'; ref=-1; founder=False; autonomous=False; bridge=False
            else:
                self.bought[i]=True; self.first_month[i]=month; new_ids.append(i)
                self.satisfaction[i]=np.clip(.65*c.product_quality+.35*S.fit[i]+satisfaction_noise[i]-congestion,0,1)
                self.energy[i]=1. if self.satisfaction[i]>=c.promoter_threshold else 0.
                ref=int(self.origin_referrer[i]); origin=CHANNELS[self.origin[i]]
                founder=bool(self.founder_ever[i]); autonomous=bool(self.origin[i]==4 and not founder)
                bridge=bool(ref>=0 and S.community[ref]!=S.community[i])
                self.acquisition_founder[i]=founder; self.acquisition_autonomous[i]=autonomous; self.acquisition_bridge[i]=bridge
                auto_count+=autonomous; founder_new+=founder; bridge_count+=bridge; by_channel[self.origin[i]]+=1
            self.sales.append(dict(seed=self.seed,strategy=self.strategy,month=month,person_id=i,
                purchase_type='repeat' if repeat else 'first',origin=origin,origin_month=0 if repeat else int(self.origin_month[i]),
                referrer=ref,community=int(S.community[i]),external=int(not S.initial[i]),
                founder_involved=int(founder),autonomous=int(autonomous),bridging=int(bridge)))

        # Synchronous decay, with no new customer recommending in the purchase month.
        old_founder=self.founder.copy()
        decaying=(self.founder>0)&~interacted
        self.founder[decaying]=np.maximum(0,self.founder[decaying]-c.tie_decay)
        self.founder[self.founder<c.tie_threshold]=0
        for i in np.flatnonzero((old_founder>0)&(self.founder==0)):
            self.log_link(month,-1,i,'founder','removed',0,'decay')
        for key in list(self.referral_links):
            if key not in commercial_interactions:self.referral_links[key]=max(0,self.referral_links[key]-c.tie_decay)
            if self.referral_links[key]<c.tie_threshold:
                del self.referral_links[key]; self.log_link(month,*key,'referral','removed',0,'decay')
        self.energy=np.maximum(0,self.energy-c.energy_decay)
        active=self.bought & ((month-self.last_purchase)<c.active_months)
        active_count=int(active.sum()); total=int(self.bought.sum()); new_count=len(new_ids)
        community_counts=np.bincount(S.community[active],minlength=c.communities)
        reached=int((community_counts>0).sum()); shares=community_counts[community_counts>0]/max(1,active_count)
        diversity=float(-(shares*np.log(shares)).sum()/math.log(c.communities)) if c.communities>1 and active_count else 0.
        spent=used*action_costs; sales=len(accepted); self.cumulative_sales+=sales; self.cumulative_autonomous+=auto_count
        assert float(spent.sum())<=hours+1e-8
        assert total<=n and sales<=c.capacity and np.all((self.founder>=0)&(self.founder<=1))
        row=dict(seed=self.seed,strategy=self.strategy,month=month,new_customers=new_count,
            repurchases=repeat_count,sales=sales,cumulative_sales=self.cumulative_sales,
            cumulative_customers=total,active_customers=active_count,net_active_growth=active_count-self.previous_active,
            external_customers=int((self.bought&~S.initial).sum()),external_share=ratio((self.bought&~S.initial).sum(),total),
            autonomous_new=auto_count,autonomous_share=ratio(auto_count,new_count),cumulative_autonomous=self.cumulative_autonomous,
            founder_new=founder_new,founder_acquisition_share=ratio(founder_new,new_count),founder_sales_share=ratio(founder_new,sales),
            direct_origin_new=by_channel[1],exploration_origin_new=by_channel[2],requested_origin_new=by_channel[3],wom_origin_new=by_channel[4],
            customer_origin_share=ratio(by_channel[3]+by_channel[4],new_count),bridging_new=bridge_count,
            communities_reached=reached,community_diversity=diversity,
            initial_saturation=float(self.approached_initial[S.initial].mean()),
            founder_degree=int((self.founder>0).sum()),mean_founder_tie_strength=float(self.founder[self.founder>0].mean()) if (self.founder>0).any() else 0.,
            active_referral_links=len(self.referral_links),active_promoters=int((active&(self.satisfaction>=c.promoter_threshold)&(self.energy>0)).sum()),
            requested_exposures=sum(e[1]==3 for e in exposures),spontaneous_exposures=sum(e[1]==4 for e in exposures),
            hours_budget=hours,hours_used=float(spent.sum()),hours_unused=float(hours-spent.sum()),
            hours_sell=float(spent[0]),hours_maintain=float(spent[1]),hours_refer=float(spent[2]),hours_explore=float(spent[3]),
            unmet_demand=unmet,graph_fingerprint=S.fingerprint)
        eligible_autonomy=autonomy_criteria(row,c)
        self.streak=self.streak+1 if eligible_autonomy else 0
        achieved=self.streak>=c.autonomy_months
        if achieved and not self.first_autonomy:self.first_autonomy=month
        self.autonomy_periods+=int(achieved)
        row.update(autonomy_criteria_met=int(eligible_autonomy),autonomy_streak=self.streak,autonomy_active=int(achieved))
        self.periods.append(row); self.previous_active=active_count
        if self.trace and month in (12,30,c.months):self.snapshot(month)

    def run(self):
        for month in range(1,self.c.months+1):self.step(month)
        last=self.periods[-1]
        summary=dict(seed=self.seed,strategy=self.strategy,graph_fingerprint=self.init.fingerprint,
            early_sales=sum(r['sales'] for r in self.periods if r['month']<=12),total_sales=last['cumulative_sales'],
            unique_customers=last['cumulative_customers'],active_customers_final=last['active_customers'],
            external_share_final=last['external_share'],autonomous_acquisition_share=ratio(self.cumulative_autonomous,last['cumulative_customers']),
            founder_acquisition_share=ratio(sum(r['founder_new'] for r in self.periods),last['cumulative_customers']),
            founder_sales_share=ratio(sum(r['founder_new'] for r in self.periods),last['cumulative_sales']),
            communities_final=last['communities_reached'],diversity_final=last['community_diversity'],
            autonomy_ever=int(self.first_autonomy>0),autonomy_first_month=self.first_autonomy or None,
            autonomy_censored=int(self.first_autonomy==0),autonomy_observation_month=self.first_autonomy or self.c.months,
            autonomy_periods=self.autonomy_periods,autonomy_final=last['autonomy_active'],
            hours_used=sum(r['hours_used'] for r in self.periods),hours_budget=sum(r['hours_budget'] for r in self.periods),
            founder_degree_final=last['founder_degree'],unmet_demand_total=sum(r['unmet_demand'] for r in self.periods))
        return summary

    def final_agents(self):
        for i in range(self.c.population):
            yield dict(seed=self.seed,strategy=self.strategy,person_id=i,community=int(self.init.community[i]),
                initial_network=int(self.init.initial[i]),need=float(self.init.need[i]),fit=float(self.init.fit[i]),
                ever_customer=int(self.bought[i]),first_purchase_month=int(self.first_month[i]) or None,
                last_purchase_month=int(self.last_purchase[i]) if self.bought[i] else None,
                active_final=int(self.bought[i] and self.c.months-self.last_purchase[i]<self.c.active_months),
                origin=CHANNELS[self.origin[i]],origin_month=int(self.origin_month[i]) or None,
                founder_contact_ever=int(self.founder_ever[i]),founder_at_acquisition=int(self.acquisition_founder[i]),
                autonomous_acquisition=int(self.acquisition_autonomous[i]),bridging_acquisition=int(self.acquisition_bridge[i]),
                contacts_received=int(self.contact_count[i]),satisfaction=float(self.satisfaction[i]) if self.bought[i] else None,
                energy=float(self.energy[i]),founder_tie_strength=float(self.founder[i]))
