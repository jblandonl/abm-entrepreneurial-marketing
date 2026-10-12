"""Run a paired-seed pilot, save complete records and one prespecified trace."""
from pathlib import Path
from dataclasses import asdict
import argparse, json, platform, time
import numpy as np
import pandas as pd
from model import Config, Model, STRATEGIES, VERSION, make_initial

def save_csv(rows,path):
    pd.DataFrame(rows).to_csv(path,index=False,encoding='utf-8-sig',float_format='%.10g')

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--repetitions',type=int,default=30)
    ap.add_argument('--seed-start',type=int,default=1001)
    ap.add_argument('--config',default='config.json')
    ap.add_argument('--output',default='results')
    args=ap.parse_args(); assert args.repetitions>0
    config_path=Path(args.config)
    if not config_path.is_file():raise SystemExit(f'No se encontró la configuración: {config_path}')
    c=Config(**json.loads(config_path.read_text('utf-8')))
    c.validate(); out=Path(args.output)
    if out.exists() and any(out.iterdir()):
        raise SystemExit('La carpeta de salida contiene archivos. Use --output con una carpeta nueva para conservar los datos originales.')
    out.mkdir(parents=True,exist_ok=True)
    (out/'config_used.json').write_text(json.dumps(asdict(c),indent=2),encoding='utf-8')
    summaries=[]; periods=[]; sales=[]; agents=[]; snapshot_nodes=[]; snapshot_referrals=[]
    link_events=[]; exposures=[]; start=time.time()
    seeds=list(range(args.seed_start,args.seed_start+args.repetitions))
    for rep,seed in enumerate(seeds,1):
        initial=make_initial(c,seed)
        for key in STRATEGIES:
            trace=seed==seeds[0]
            m=Model(c,seed,key,trace=trace,initial=initial)
            summaries.append(m.run()); periods.extend(m.periods); sales.extend(m.sales); agents.extend(m.final_agents())
            if trace:
                link_events.extend(m.link_events); exposures.extend(m.exposure_events)
                for snap in m.snapshots:
                    for i in range(c.population):
                        snapshot_nodes.append(dict(seed=seed,strategy=key,month=snap['month'],person_id=i,
                            community=int(initial.community[i]),initial_network=int(initial.initial[i]),
                            customer=int(snap['bought'][i]),active=int(snap['active'][i]),
                            founder_strength=float(snap['founder'][i]),energy=float(snap['energy'][i]),
                            satisfaction=float(snap['satisfaction'][i])))
                    for (source,target),strength in snap['referral_links'].items():
                        snapshot_referrals.append(dict(seed=seed,strategy=key,month=snap['month'],source=source,target=target,strength=strength))
        if seed==seeds[0]:
            edges=np.transpose(np.nonzero(np.triu(initial.social,1)))
            save_csv([dict(seed=seed,source=int(i),target=int(j),strength=initial.social_strength[i,j],
                           bridging=int(initial.community[i]!=initial.community[j])) for i,j in edges],out/'social_edges_trace.csv')
        if rep%10==0 or rep==args.repetitions:print(f'{rep}/{args.repetitions} semillas completas',flush=True)
    for name,rows in [('simulation_summary',summaries),('system_month',periods),('purchase_events',sales),
                      ('agents_final',agents),('nodes_trace',snapshot_nodes),('referral_edges_trace',snapshot_referrals),
                      ('link_events_trace',link_events),('exposures_trace',exposures)]:
        save_csv(rows,out/f'{name}.csv')
    meta=dict(model_version=VERSION,scope='exploratory pilot; uncalibrated',repetitions_per_strategy=args.repetitions,
              seeds=seeds,trace_seed=seeds[0],months=c.months,population=c.population,strategies=list(STRATEGIES),
              simulation_count=len(summaries),python=platform.python_version(),numpy=np.__version__,pandas=pd.__version__,
              elapsed_seconds=round(time.time()-start,3))
    (out/'run_metadata.json').write_text(json.dumps(meta,indent=2),encoding='utf-8')
    print(json.dumps(meta,ensure_ascii=False),flush=True)

if __name__=='__main__':main()
