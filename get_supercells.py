from utils.material import material
from utils.screen import get_median
from dirs import *

subid = '1'
ndim = 2
# the mpids which has already run in ryotaro's account. We exclude these from job lists. 
skips1 = sorted([1002124, 1087, 149, 1672, 21511, 315, 441, 5072, 632319, 866291, 
                10044, 1253, 149, 1700, 241, 370, 463, 571386, 684580, 9564, 
                10627, 1315, 1500, 2064, 30373, 370, 4961, 573697, 8455])
# the mpids which has already run in qcsong's account. We exclude these from job lists. 
skips2 = sorted([1000, 149, 21511, 22862, 22919, 406, 568560, 8062, 8455, 997618_1, 
                1022, 149, 2251, 22865, 2758, 422, 614603, 830, 866291, 
                1029, 2074, 22851, 22916, 2853, 4961, 682, 8454, 997618])
skips = skips1+skips2
with open(mpids_file, 'r') as f:
    mpids = f.readlines()
mpids = sorted([int(mpid[:-1]) for mpid in mpids])
print(mpids)
print('mpid: ', len(mpids))
# mpids = sorted([int(mpid) for mpid in mpids if mpid <= get_median(mpids)])
print(mpids)
print('mpid: ', len(mpids))

for mpid in mpids: 
    if int(mpid) not in skips:
        mpid = str(mpid)
        print(mpid)
        m1 = material(mpid,subid,nomaddir,jobdir,psdir)
        m1.get_abinit_vars()
        m1.gen_header(ndim,ndim,ndim)
        m1.run_phono3py()
    else:
        print("skip: ", mpid)

