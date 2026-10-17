(* Public MAST data only. Re-querying creates a new archive snapshot. *)
u="https://archive.stsci.edu/missions/tess/tid/s0004/0000/0002/5937/7017/tess2018292075959-s0004-0000000259377017-0124-s_lc.fits";
f=CreateTemporary[]; URLDownload[u,f];
sha=FileHash[f,"SHA256","HexString"];
d=Import[f,{"FITS","Data",2}];
v=Select[d,And@@(NumberQ/@#[[{1,4,8,10}]])&&#[[10]]==0&&#[[4]]>0&&#[[8]]>0&];
g=Select[GatherBy[v,Floor[48#[[1]]]&],Length[#]>=10&];
a=({Mean[#[[All,1]]],Mean[#[[All,4]]],Mean[#[[All,8]]]}&/@g);
sm=Median[a[[All,2]]]; pm=Median[a[[All,3]]];
z=({Round[1000000#[[1]]],Round[1000000(#[[2]]/sm-1)],Round[1000000(#[[3]]/pm-1)]}&/@a);
Export["toi270_s4_binned.csv",z,"CSV"];
{sha,Dimensions[d],Length[v],Length[z],Total[Length/@g],sm,pm}
(* Catalog comparison was queried AFTER the local search completed. *)
q="SELECT pl_name,hostname,pl_orbper,pl_rade,tic_id FROM pscomppars WHERE tic_id='TIC 259377017'";
Import["https://exoplanetarchive.ipac.caltech.edu/TAP/sync?query="<>URLEncode[q]<>"&format=csv","Text"]
