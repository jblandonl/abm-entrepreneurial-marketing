"""Reproduce descriptive summaries, paired comparisons and pilot figures."""
from pathlib import Path
import argparse, json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.lines import Line2D
from model import Config, STRATEGIES

COLORS={'A':'#3D5A80','B':'#D07A35','C':'#24867D','D':'#8B5DA6'}
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,
    'axes.spines.right':False,'axes.titleweight':'bold','svg.fonttype':'none'})

def save(df,path):df.to_csv(path,index=False,encoding='utf-8-sig',float_format='%.10g')

def verify_exports(summary,monthly,events,agents):
    assert len(summary)==len(summary[['seed','strategy']].drop_duplicates())
    assert monthly.groupby(['seed','strategy']).size().nunique()==1
    assert (summary.groupby('seed').graph_fingerprint.nunique()==1).all()
    assert (monthly.hours_used<=monthly.hours_budget+1e-8).all()
    assert (monthly.sales==monthly.new_customers+monthly.repurchases).all()
    first=events.query("purchase_type=='first'")
    assert not first.duplicated(['seed','strategy','person_id']).any()
    for key,s in summary.set_index(['seed','strategy']).iterrows():
        seed,strategy=key
        ev=events[(events.seed==seed)&(events.strategy==strategy)]
        ag=agents[(agents.seed==seed)&(agents.strategy==strategy)]
        assert len(ev)==s.total_sales
        assert int(ag.ever_customer.sum())==s.unique_customers==int((ev.purchase_type=='first').sum())
    assert ((first.autonomous==0)|((first.origin=='spontaneous_wom')&(first.founder_involved==0))).all()

def network_figure(raw,out,seed):
    nodes=pd.read_csv(raw/'nodes_trace.csv'); edges=pd.read_csv(raw/'social_edges_trace.csv')
    referrals=pd.read_csv(raw/'referral_edges_trace.csv')
    base=nodes[(nodes.strategy=='D')&(nodes.month==0)].sort_values('person_id')
    community=base.community.to_numpy(); n=len(base); k=int(community.max())+1
    rng=np.random.default_rng(seed)
    group_angles=np.linspace(0,2*np.pi,k,endpoint=False)+np.pi/2
    centers=np.column_stack([np.cos(group_angles),np.sin(group_angles)])*3
    angles=rng.uniform(0,2*np.pi,n); radii=np.sqrt(rng.uniform(0,1,n))*.98
    pos=centers[community]+np.column_stack([radii*np.cos(angles),radii*np.sin(angles)])
    palette=np.array(['#3274A1','#DD8452','#55A868','#C44E52','#8172B3'])
    fig,axs=plt.subplots(1,3,figsize=(13.6,5))
    available=sorted(nodes.month.unique())
    selected=[0,12 if 12 in available else available[len(available)//2],available[-1]]
    for ax,month in zip(axs,selected):
        d=nodes[(nodes.strategy=='D')&(nodes.month==month)].sort_values('person_id')
        if d.empty:ax.axis('off');continue
        seg=pos[edges[['source','target']].to_numpy(int)]
        ax.add_collection(LineCollection(seg,colors='#D7DDE2',linewidths=.22,alpha=.4,zorder=0))
        active_links=d[d.founder_strength>0].person_id.to_numpy(int)
        ax.add_collection(LineCollection([[np.zeros(2),pos[i]] for i in active_links],colors='#35556C',linewidths=.45,alpha=.26,zorder=1))
        rr=referrals[(referrals.strategy=='D')&(referrals.month==month)]
        if len(rr):ax.add_collection(LineCollection(pos[rr[['source','target']].to_numpy(int)],colors='#C67C2E',linewidths=.65,alpha=.6,zorder=2))
        colors=np.where(d.customer.to_numpy(bool)[:,None],np.array([matplotlib.colors.to_rgb(x) for x in palette[community%5]]),matplotlib.colors.to_rgb('#D4DADF'))
        ax.scatter(pos[:,0],pos[:,1],s=11,c=colors,edgecolors='white',linewidths=.15,zorder=3)
        initial=d.initial_network.to_numpy(bool)
        ax.scatter(pos[initial,0],pos[initial,1],s=20,facecolors='none',edgecolors='#273C4B',linewidths=.45,zorder=4)
        ax.scatter([0],[0],marker='*',s=160,c='#102C40',zorder=5)
        customers=int(d.customer.sum()); external=int(((d.customer==1)&(d.initial_network==0)).sum())
        ax.set_title(f'Mes {month}\n{customers} clientes únicos · {external} externos',fontsize=11)
        ax.set_aspect('equal');ax.set_xlim(-4.3,4.3);ax.set_ylim(-4.3,4.3);ax.axis('off')
    fig.suptitle(f'Evolución de la red · estrategia D · semilla {seed}',fontsize=16,fontweight='bold',y=.98)
    handles=[Line2D([0],[0],marker='*',color='none',markerfacecolor='#102C40',markersize=11,label='Fundador'),
        Line2D([0],[0],marker='o',color='none',markerfacecolor='#D4DADF',markersize=6,label='No ha comprado'),
        Line2D([0],[0],marker='o',color='none',markerfacecolor='#3274A1',markersize=6,label='Cliente: color por comunidad'),
        Line2D([0],[0],marker='o',color='none',markerfacecolor='none',markeredgecolor='#273C4B',markersize=6,label='Contacto inicial'),
        Line2D([0],[0],color='#35556C',label='Vínculo del fundador'),Line2D([0],[0],color='#C67C2E',label='Referido activo')]
    fig.legend(handles=handles,loc='lower center',ncol=3,frameon=False,fontsize=9,bbox_to_anchor=(.5,.03))
    fig.text(.5,.012,'Ejemplo prespecificado; no representa el promedio. Posiciones y red social de fondo idénticas en los tres momentos.',ha='center',fontsize=9,color='#526777')
    fig.subplots_adjust(top=.78,bottom=.23,wspace=.06)
    fig.savefig(out/'02_network_example.png',dpi=300,bbox_inches='tight')
    fig.savefig(out/'02_network_example.svg',bbox_inches='tight');plt.close(fig)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--input',default='results');args=ap.parse_args()
    raw=Path(args.input);out=raw/'analysis';out.mkdir(exist_ok=True)
    s=pd.read_csv(raw/'simulation_summary.csv'); m=pd.read_csv(raw/'system_month.csv')
    ev=pd.read_csv(raw/'purchase_events.csv'); ag=pd.read_csv(raw/'agents_final.csv')
    verify_exports(s,m,ev,ag)
    cfg=Config(**json.loads((raw/'config_used.json').read_text()))
    metrics=['early_sales','total_sales','unique_customers','active_customers_final','external_share_final',
             'autonomous_acquisition_share','founder_acquisition_share','founder_sales_share','communities_final',
             'diversity_final','hours_used','founder_degree_final','autonomy_ever']
    rows=[]
    for key,g in s.groupby('strategy'):
        for metric in metrics:
            x=g[metric].dropna()
            rows.append(dict(strategy=key,metric=metric,n=len(x),mean=x.mean(),median=x.median(),
                             sd=x.std(ddof=1),p05=x.quantile(.05),p95=x.quantile(.95),min=x.min(),max=x.max()))
    save(pd.DataFrame(rows),out/'descriptive_statistics.csv')
    student=s.groupby('strategy')[metrics].mean().reset_index()
    student.insert(1,'label',student.strategy.map({k:v[0] for k,v in STRATEGIES.items()}))
    save(student,out/'strategy_means.csv')

    # Resample seed-level differences, not monthly rows, for Monte Carlo uncertainty.
    comparisons=[];rg=np.random.default_rng(63017)
    for metric in metrics[:8]:
        wide=s.pivot(index='seed',columns='strategy',values=metric)
        for key in 'BCD':
            delta=(wide[key]-wide['A']).dropna().to_numpy()
            boot=delta[rg.integers(0,len(delta),size=(2000,len(delta)))].mean(axis=1)
            comparisons.append(dict(comparison=f'{key}-A',metric=metric,n_seed_pairs=len(delta),
                mean_difference=delta.mean(),ci95_low=np.quantile(boot,.025),ci95_high=np.quantile(boot,.975)))
    save(pd.DataFrame(comparisons),out/'paired_differences.csv')

    # One-at-a-time reclassification, not additional simulations or behavioral sensitivity.
    thresholds=[]
    for variable in ['autonomous_share','external_share','founder_sales_share']:
        for level in [.4,.5,.6]:
            for (seed,key),g in m.groupby(['seed','strategy'],sort=True):
                a=level if variable=='autonomous_share' else cfg.autonomy_share
                x=level if variable=='external_share' else cfg.autonomy_external
                d=level if variable=='founder_sales_share' else cfg.autonomy_dependency
                mask=(g.new_customers>0)&(g.autonomous_share>a)&(g.external_share>x)&(g.founder_sales_share<d)&(g.net_active_growth>0)&(g.communities_reached>=cfg.autonomy_communities)
                streak=0;first=None
                for month,ok in zip(g.month,mask):
                    streak=streak+1 if ok else 0
                    if streak>=cfg.autonomy_months and first is None:first=int(month)
                thresholds.append(dict(seed=seed,strategy=key,varied_threshold=variable,value=level,
                    autonomy_ever=int(first is not None),first_confirmation_month=first))
    save(pd.DataFrame(thresholds),out/'autonomy_thresholds.csv')

    # Rolling ratios pool counts within each run; blanks remain undefined, never zero-filled.
    sm=[]
    for _,g in m.groupby(['seed','strategy'],sort=False):
        g=g.sort_values('month').copy()
        for col,num,den in [('autonomous_6m','autonomous_new','new_customers'),('founder_acquisition_6m','founder_new','new_customers')]:
            g[col]=g[num].rolling(6,min_periods=1).sum()/g[den].rolling(6,min_periods=1).sum().replace(0,np.nan)
        sm.append(g)
    mm=pd.concat(sm,ignore_index=True)
    plot_metrics=[('cumulative_sales','Ventas acumuladas (incluye recompras)',False),
        ('cumulative_customers','Clientes únicos acumulados',False),('external_share','Clientes externos / clientes acumulados',True),
        ('autonomous_6m','Adquisición autónoma · ventana de 6 meses',True),
        ('founder_acquisition_6m','Adquisición dependiente · ventana de 6 meses',True),
        ('active_customers','Clientes activos',False)]
    fig,axes=plt.subplots(2,3,figsize=(14,8))
    curves=[]
    for ax,(metric,title,pct) in zip(axes.flat,plot_metrics):
        for key,g in mm.groupby('strategy'):
            gg=g.groupby('month')[metric]; mean=gg.mean(); low=gg.quantile(.1);high=gg.quantile(.9)
            ax.plot(mean.index,mean,color=COLORS[key],lw=2,label=f'{key} · {STRATEGIES[key][0]}')
            ax.fill_between(mean.index,low,high,color=COLORS[key],alpha=.10,linewidth=0)
            for month in mean.index:curves.append(dict(strategy=key,month=month,metric=metric,mean=mean.loc[month],p10=low.loc[month],p90=high.loc[month],n_valid=int(gg.count().loc[month])))
        ax.set_title(title,fontsize=11);ax.set_xlabel('Mes');ax.grid(alpha=.18)
        if pct:
            from matplotlib.ticker import PercentFormatter
            ax.yaxis.set_major_formatter(PercentFormatter(1));ax.set_ylim(0,1)
    handles,labels=axes[0,0].get_legend_handles_labels();fig.legend(handles,labels,loc='lower center',ncol=4,frameon=False,bbox_to_anchor=(.5,.015))
    fig.suptitle('Piloto exploratorio · cuatro estrategias de networking',fontsize=17,fontweight='bold',y=.99)
    fig.text(.5,.935,f'{s.seed.nunique()} réplicas por estrategia · {cfg.population} personas · {cfg.months} meses · parámetros sin calibración empírica',ha='center',fontsize=11,color='#526777')
    fig.text(.5,.068,'Líneas: medias entre réplicas. Bandas: percentiles 10–90; no son intervalos de confianza ni evidencia de empresas reales.',ha='center',fontsize=9,color='#526777')
    fig.tight_layout(rect=[0,.1,1,.91])
    fig.savefig(out/'01_pilot_overview.png',dpi=300,bbox_inches='tight');fig.savefig(out/'01_pilot_overview.svg',bbox_inches='tight');plt.close(fig)
    save(pd.DataFrame(curves),out/'plot_data.csv')
    network_figure(raw,out,int(s.seed.min()))
    (out/'export_verification.json').write_text(json.dumps(dict(status='passed',simulations=len(s),monthly_rows=len(m),
        purchase_events=len(ev),final_agent_rows=len(ag),initial_conditions_paired=True,unique_first_purchases=True,
        monthly_accounting_reconciles=True,autonomous_provenance_valid=True),indent=2),encoding='utf-8')
    print(student.to_string(index=False))

if __name__=='__main__':main()
