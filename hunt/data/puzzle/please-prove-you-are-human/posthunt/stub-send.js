const IMAGES_REQUIRED = 9;
const IMAGE_DATA = {"LAKE":{"RFy2rA2m":[1,0,0],"13icV6gm":[1,0,0],"dEZ4ARtm":[1,0,0],"Ye1DfQ3m":[1,0,0],"ISEWnNhm":[1,0,0],"JPb7Gd2m":[1,0,0],"Y2GntgSm":[0,1,1],"XtVzhxym":[0,1,1],"r7LfNWam":[0,1,1],"tH3j4L7m":[0,1,1],"PZq7JCIm":[0,1,1],"44PdIGfm":[0,1,1],"tIgPv7Cm":[0,1,0],"ZyEdzb8m":[0,1,0],"S4XaK7Am":[0,1,0],"bzOHG8bm":[0,1,0],"YFBhloJm":[0,1,0],"H9sd3axm":[0,1,0]},"ISLAND":{"BaHGXx8m":[1,0,0],"2vRtxcam":[1,0,0],"zHWYbcvm":[1,0,0],"vJdv0abm":[1,0,0],"J1xSY0em":[1,0,0],"wEDYCxSm":[1,0,0],"J7v7WlXm":[0,1,1],"NXYwG4fm":[0,1,1],"zy4thckm":[0,1,1],"S5m9gfym":[0,1,1],"1B7m7hum":[0,1,1],"fZhbDEhm":[0,1,1],"KEFu2I9m":[0,1,0],"7jEvoPIm":[0,1,0],"Ig2SGsLm":[0,1,0],"4pbtMXYm":[0,1,0],"0xlzJpum":[0,1,0],"uSvGCIrm":[0,1,0]},"BECUNA":{"gjuqNQKm":[0,1,1],"DkgpYx3m":[0,1,1],"maUeXI7m":[0,1,1],"tNpWuE4m":[0,1,1],"ofmg3x4m":[0,1,1],"zIQ547Rm":[0,1,1],"SwmwqqKm":[0,1,1],"BNAuy7Lm":[0,1,1],"D2o1CqAm":[0,1,0],"vjm9vShm":[0,1,0],"ttv8dism":[0,1,0],"b2MNIsmm":[0,1,0],"qLD0BhGm":[0,1,0],"oxHXS0Om":[0,1,0],"ITjltFEm":[1,0,0],"oDEdkoYm":[1,0,0],"Wutc8OWm":[1,0,0],"sz55pYdm":[1,0,0],"G3U1beRm":[1,0,0]},"SHELL":{"amHZPprm":[1,0,0],"5zrH1CAm":[1,0,0],"CHhDitpm":[1,0,0],"OFGWzXom":[1,0,0],"OwVAQ2gm":[1,0,0],"2MWEjZ1m":[1,0,0],"drN8JcLm":[0,1,1],"TFtQuPzm":[0,1,1],"4pYQLtFm":[0,1,1],"X7rQhRjm":[0,1,1],"pZHSMb4m":[0,1,1],"hkMy8Mjm":[0,1,1],"lnTBzGDm":[0,1,0],"4xFx1kPm":[0,1,0],"YGrAjabm":[0,1,0],"CkW3BYRm":[0,1,0],"TG8sdRpm":[0,1,0],"TiAfodjm":[0,1,0]},"BEZOAR":{"J4zoqE4m":[0,1,1],"zm8tdyOm":[0,1,1],"ckuZkpjm":[0,1,1],"F40ZsrDm":[0,1,1],"Z4ZPluTm":[0,1,1],"pjyabtzm":[0,1,1],"22nDxG7m":[0,1,1],"BBh0kj2m":[0,1,1],"wAFUiBUm":[0,1,0],"S8jeFUHm":[0,1,0],"qNQZl7Cm":[0,1,0],"yf7ye2Zm":[0,1,0],"i8LCqVZm":[0,1,0],"wI3uqmzm":[0,1,0],"1n6LBuzm":[0,1,0],"XLVErQgm":[0,1,0],"9NiVNEvm":[1,0,0],"oAFyQz5m":[1,0,0],"dM9o2vYm":[1,0,0],"D8vklUEm":[1,0,0],"TgESFpMm":[1,0,0],"roJaXUYm":[1,0,0],"8gRcq5mm":[1,0,0],"pgTa1clm":[1,0,0]},"TABLE":{"gxV8CU0m":[1,0,0],"Otczv1km":[1,0,0],"6LITxMkm":[1,0,0],"1su8vTnm":[1,0,0],"eF5LU61m":[1,0,0],"4dBdPWLm":[1,0,0],"69b5bQ1m":[0,1,1],"ciu0aShm":[0,1,1],"1YO0kiGm":[0,1,1],"ZfJx1ddm":[0,1,1],"d7pfnNsm":[0,1,1],"wA7GQHjm":[0,1,1],"DGsevzgm":[0,1,0],"9QUxQgRm":[0,1,0],"uI716Mcm":[0,1,0],"aCmkPOam":[0,1,0],"PzDrcNrm":[0,1,0],"ZTKbyaxm":[0,1,0]},"EGG":{"C53TM1jm":[1,0,0],"J5RqSPUm":[1,0,0],"7pAIaSFm":[1,0,0],"uc7RCW5m":[1,0,0],"vM4Fl4um":[1,0,0],"ELhMOvKm":[1,0,0],"ggQfhodm":[0,1,1],"JgRfjhGm":[0,1,1],"fIN0Oyzm":[0,1,1],"ZWlaxvTm":[0,1,1],"VYbeTrim":[0,1,1],"4nj9dWRm":[0,1,1],"tqNKcC1m":[0,1,0],"VolEtedm":[0,1,0],"L0vT0dEm":[0,1,0],"ZhKtxHkm":[0,1,0],"xy1cYK1m":[0,1,0],"mcOCZEFm":[0,1,0]},"AGLET":{"zGO4nk1m":[0,1,1],"b6gKEm5m":[0,1,1],"wVz6CyBm":[0,1,1],"VANfvSDm":[0,1,1],"1ILEzWEm":[0,1,1],"qGbhlLim":[0,1,1],"AwMtNd1m":[0,1,1],"aqIExRam":[0,1,1],"AlymPH1m":[0,1,0],"QWCsb5Zm":[0,1,0],"5RYe2NSm":[0,1,0],"Mq4L1G0m":[0,1,0],"PbSfhQUm":[0,1,0],"m8IJJTGm":[0,1,0],"mvzbOBDm":[0,1,0],"ctmXaivm":[0,1,0],"rXSglq4m":[1,0,0],"BL3XQmgm":[1,0,0],"SvsJo5sm":[1,0,0],"nTqXPLrm":[1,0,0],"iOYJ2mnm":[1,0,0],"SG7Gjuxm":[1,0,0],"AN5NLLqm":[1,0,0],"ns2g4gIm":[1,0,0]},"NOTEBOOK":{"8yQElVdm":[1,0,0],"0jmIS8gm":[1,0,0],"SM8LD3Xm":[1,0,0],"lxiOAFfm":[1,0,0],"lghwoNhm":[1,0,0],"1FzTJXNm":[1,0,0],"JHLFBSRm":[0,1,1],"4K3Y1g0m":[0,1,1],"juKMTeLm":[0,1,1],"K5ABBKGm":[0,1,1],"UHSY7J3m":[0,1,1],"wfzb12Tm":[0,1,1],"LTLK8Csm":[0,1,0],"BFiwktkm":[0,1,0],"3ymnUcUm":[0,1,0],"dN3EBdnm":[0,1,0],"ZFYtIXTm":[0,1,0],"7frKXaNm":[0,1,0]},"TRAP":{"URqkjXam":[1,0,0],"ZknrsFrm":[1,0,0],"H8ASvPQm":[1,0,0],"bhgxMlTm":[1,0,0],"3LNvHNJm":[1,0,0],"uPK8YoGm":[1,0,0],"mPZdONMm":[0,1,1],"zfh72R8m":[0,1,1],"Br0T9tfm":[0,1,1],"L1bGOXOm":[0,1,1],"fIxExO8m":[0,1,1],"yFtk6XUm":[0,1,1],"RceeWHUm":[0,1,0],"stfCsUgm":[0,1,0],"KnS63YMm":[0,1,0],"sE50sP5m":[0,1,0],"o8s3GGom":[0,1,0],"tcbFdtbm":[0,1,0]},"IRONSAND":{"5H5ZEIrm":[1,0,0],"henJpJbm":[1,0,0],"V5k0OPLm":[1,0,0],"nLhSm20m":[1,0,0],"rCUDYAwm":[1,0,0],"Qloua23m":[1,0,0],"pcFFVY1m":[0,1,1],"GtuUllvm":[0,1,1],"Nvz3o2Cm":[0,1,1],"7DdBUMSm":[0,1,1],"dbbtAnom":[0,1,1],"cRp05fTm":[0,1,1],"i4V0CHTm":[0,1,0],"v2mj3Xum":[0,1,0],"52OSPbMm":[0,1,0],"tMyXMhym":[0,1,0],"8y1LGNVm":[0,1,0],"yIMp2IHm":[0,1,0]},"WOLF":{"xE8MQfAm":[1,0,0],"iij3bjdm":[1,0,0],"3KOB0VEm":[1,0,0],"SAkSGqtm":[1,0,0],"3J1P5YBm":[1,0,0],"Via8EUGm":[1,0,0],"Z7Os1Wgm":[0,1,1],"LzE9DwDm":[0,1,1],"5pzY52Qm":[0,1,1],"D2pQLdxm":[0,1,1],"Dlak4emm":[0,1,1],"5Vv5JWxm":[0,1,1],"gHAREzmm":[0,1,0],"d3lY4Bxm":[0,1,0],"D7TQkhNm":[0,1,0],"hIprD6qm":[0,1,0],"lTEEfHRm":[0,1,0],"nRn2UCSm":[0,1,0]},"ORGAN":{"NCHwT5im":[1,0,0],"1Yil55am":[1,0,0],"GoDNYiFm":[1,0,0],"ccKvFTcm":[1,0,0],"7mYSm8zm":[1,0,0],"ESH2Pgfm":[1,0,0],"EdEXLtsm":[0,1,1],"Pvtf8Pam":[0,1,1],"PChKbcVm":[0,1,1],"odgrKpam":[0,1,1],"7fD2kjqm":[0,1,1],"JsKE3OPm":[0,1,1],"nJL8qBTm":[0,1,0],"0BSgzDKm":[0,1,0],"I3EQpBJm":[0,1,0],"dHCY7g2m":[0,1,0],"z9voORWm":[0,1,0],"X5zdvN5m":[0,1,0]},"BONE":{"rjI4LLDm":[1,0,0],"JjN6fGDm":[1,0,0],"zB5INsHm":[1,0,0],"PgGix21m":[1,0,0],"ZxMbxezm":[1,0,0],"T0xO0Frm":[1,0,0],"FUaFfkhm":[0,1,1],"H6okqbPm":[0,1,1],"metFggXm":[0,1,1],"PC9BJAHm":[0,1,1],"lu3Ykh1m":[0,1,1],"FWsdLepm":[0,1,1],"kC0STMfm":[0,1,0],"5Ko8SSGm":[0,1,0],"hoZz23im":[0,1,0],"i75LNiLm":[0,1,0],"sbUdcQkm":[0,1,0],"D6AMlYRm":[0,1,0]},"PAN":{"FqpHNY8m":[1,0,0],"PFHcHXXm":[1,0,0],"72KP0sKm":[1,0,0],"34x75kQm":[1,0,0],"hascxw0m":[1,0,0],"m4UIWtrm":[1,0,0],"7vbYoa0m":[0,1,1],"PxZGSzlm":[0,1,1],"tx66jy4m":[0,1,1],"4ibHJ4Ym":[0,1,1],"XSHdK4Dm":[0,1,1],"dFD6HpRm":[0,1,1],"RQqsrr7m":[0,1,0],"HaSjCmkm":[0,1,0],"mV1nfjtm":[0,1,0],"W9VW9GPm":[0,1,0],"4Vtcudwm":[0,1,0],"koAWnBHm":[0,1,0]},"RABBIT":{"QJRvTB4m":[1,0,0],"no6M0GQm":[1,0,0],"1TLdUBlm":[1,0,0],"gg9CYq7m":[1,0,0],"HRGbHfmm":[1,0,0],"CxMaBgJm":[1,0,0],"hSpUpsCm":[0,1,1],"u7M9Agrm":[0,1,1],"9J370GXm":[0,1,1],"fAUvR6em":[0,1,1],"X9rAk0im":[0,1,1],"TwYsc8ym":[0,1,1],"ecYgqlgm":[0,1,0],"cVQyeqEm":[0,1,0],"HxrkSF0m":[0,1,0],"Zps8XTDm":[0,1,0],"i794El3m":[0,1,0],"yWkG5Xlm":[0,1,0]},"RANGE":{"LIQtYBqm":[1,0,0],"pMoZOF3m":[1,0,0],"A5SOnfrm":[1,0,0],"1vhrXGvm":[1,0,0],"Kf67U8Tm":[1,0,0],"QKDVZQvm":[1,0,0],"XDwpAW7m":[0,1,1],"CR6Matqm":[0,1,1],"5AYHshem":[0,1,1],"Qp0Um1am":[0,1,1],"DXadaZ0m":[0,1,1],"12nYZXBm":[0,1,1],"ymQmdD1m":[0,1,0],"jgwir4qm":[0,1,0],"XKNiW9Hm":[0,1,0],"RbeMy0Vm":[0,1,0],"4wiKjixm":[0,1,0],"xsfMWPxm":[0,1,0]},"SWORD":{"x7DqM4Um":[0,1,1],"N9Vkj3Jm":[1,0,0],"7qvTDCKm":[0,1,1],"Fu3Hgxbm":[1,0,0],"YXoGJYcm":[0,1,1],"nFAkZ5Wm":[0,1,1],"3MvLtGdm":[0,1,1],"oZ1hsggm":[0,1,1],"TpQXdpgm":[1,0,0],"lxZ70fem":[1,0,0],"WElZn75m":[1,0,0],"US3o5XEm":[1,0,0],"gFCJGA0m":[1,0,0],"LsIoM0Sm":[1,0,0],"e6tSBC0m":[1,0,0],"5T7QXjgm":[1,0,0],"YUAydwAm":[1,0,0],"T1uLhUFm":[1,0,0],"yQ7oMvHm":[0,1,1],"PBEWGg4m":[0,1,1],"V8TeUfqm":[0,1,1],"ObssuXZm":[0,1,1],"px37iqPm":[0,1,0],"RFbZarWm":[0,1,0],"V5UuueNm":[0,1,0],"oPs6QqHm":[0,1,0],"4ozVeDGm":[0,1,0],"5WmYHGNm":[0,1,0],"F0Aexg7m":[0,1,0],"05GYOnom":[0,1,0],"NhwWZFYm":[0,1,0],"KnrTCIbm":[0,1,0],"bMvQ7Yrm":[0,1,0],"gBIKBGOm":[0,1,0],"tAsPTuqm":[0,1,0],"2hyrqPdm":[0,1,0],"j3JWnPhm":[0,1,0],"n3ecOibm":[0,1,0]},"OCTOPUS":{"2WurXMvm":[1,0,0],"faXfGjFm":[1,0,0],"STyYkutm":[1,0,0],"N6rxw5wm":[1,0,0],"LrbOsgWm":[1,0,0],"rnJmbcdm":[1,0,0],"ELQsORrm":[0,1,1],"kFmGqPIm":[0,1,1],"yMiWis9m":[0,1,1],"oxf1uY9m":[0,1,1],"HPvqFhFm":[0,1,1],"ItmTPDDm":[0,1,1],"jvgcEDrm":[0,1,0],"ieYwX5Pm":[0,1,0],"OPlFqbrm":[0,1,0],"Wk6PztHm":[0,1,0],"p7hAuQNm":[0,1,0],"0CpideIm":[0,1,0]},"FIRE":{"VczcqQNm":[0,1,1],"DFzEAoom":[0,1,1],"OlL2XH6m":[1,0,0],"FZigTx1m":[1,0,0],"PFfuau1m":[0,1,1],"RaOFz91m":[0,1,1],"a6pi4lem":[0,1,1],"pb1gbsJm":[1,0,0],"fXTU6kIm":[1,0,0],"X6vLC7sm":[1,0,0],"Eym8wAnm":[1,0,0],"isttlETm":[0,1,1],"Yakt64Am":[0,1,1],"ngqG5O3m":[0,1,1],"6dXiRksm":[0,1,1],"BcxQTqSm":[0,1,0],"F24nTdTm":[0,1,0],"OQ8vgxmm":[0,1,0],"pgdUNeTm":[0,1,0],"OnYohvfm":[0,1,0],"n25jmyQm":[0,1,0],"paWO1uXm":[0,1,0],"aqr9OQzm":[0,1,0],"Pg0OAcGm":[0,1,0],"3GG2DbCm":[0,1,0],"i8z92u2m":[0,1,0],"I99c9Lfm":[0,1,0],"6vhlmHMm":[0,1,0],"EmebsT2m":[0,1,0],"yfBzNmbm":[0,1,0],"ZgV5zk2m":[0,1,0],"7nsYU26m":[0,1,0],"FHWwgSgm":[0,1,0]},"KNIFE":{"nQvK1QAm":[1,0,0],"tH1HuUym":[1,0,0],"V5VmqUtm":[1,0,0],"KGeapq0m":[1,0,0],"XsdaU9Zm":[1,0,0],"yKQswnVm":[1,0,0],"iw6iVLIm":[0,1,1],"Pr7kinvm":[0,1,1],"zVMvwPrm":[0,1,1],"78YGWy9m":[0,1,1],"Ed6UKHNm":[0,1,1],"C2O3N8zm":[0,1,1],"qgF815pm":[0,1,0],"iwXcsAqm":[0,1,0],"9nQfxFZm":[0,1,0],"ypv480em":[0,1,0],"DnZlsCxm":[0,1,0],"Jdeefb6m":[0,1,0]},"ENVELOPE":{"9GbBsqim":[1,0,0],"29ZdJ3Zm":[1,0,0],"Omwl0Fom":[1,0,0],"1R5utoNm":[1,0,0],"qTbV3SYm":[1,0,0],"96gc8r3m":[1,0,0],"ZQHCFH7m":[0,1,1],"1pjTklMm":[0,1,1],"xSGB7mum":[0,1,1],"YqcIp6wm":[0,1,1],"S9sbrcjm":[0,1,1],"Q6B1xwsm":[0,1,1],"V9OuEGfm":[0,1,0],"OWguM2Sm":[0,1,0],"6VbPHsqm":[0,1,0],"EREslX8m":[0,1,0],"I5aNizKm":[0,1,0],"UMzkTimm":[0,1,0]},"RUT":{"N3Uptx3m":[0,1,1],"UCoPahOm":[0,1,1],"mNapVP4m":[1,0,0],"Mbh3Fhqm":[0,1,1],"qih0AvHm":[0,1,1],"FyR7QMwm":[1,0,0],"vPDUFEom":[0,1,1],"AAVtVJVm":[1,0,0],"Fp5YGzym":[1,0,0],"GdBWSsOm":[1,0,0],"9Q2LWmBm":[1,0,0],"YF1n2S8m":[1,0,0],"P2Uj67nm":[1,0,0],"6TYuPxlm":[1,0,0],"AzFSIH3m":[1,0,0],"vlQ7c05m":[1,0,0],"hDAtQkbm":[0,1,1],"5NYUqsvm":[0,1,1],"5MPKXfgm":[0,1,0],"X9IMF2bm":[0,1,0],"BuAQHxGm":[0,1,0],"mgApuM5m":[0,1,0],"vhu8hhym":[0,1,0],"WVWJxebm":[0,1,0],"Sb5SZTDm":[0,1,0],"KR14yrpm":[0,1,0],"Q5E9Soxm":[0,1,0],"dU1pDUqm":[0,1,0],"4Qw5rLRm":[0,1,0],"vXg6eEMm":[0,1,0],"hlCbjHSm":[0,1,0],"JX0ueeem":[0,1,0],"uihX7o3m":[0,1,0],"NkjrgZ4m":[0,1,0],"egrmwJcm":[0,1,0]},"WORMWOOD":{"b3XS6Xym":[1,0,0],"bKwPa5vm":[0,1,1],"qhqlYqLm":[0,1,1],"KaTC3kym":[0,1,1],"WArsl8fm":[1,0,0],"VRbDvD1m":[1,0,0],"V0ZEiakm":[0,1,1],"23qZzIQm":[0,1,1],"itbcL9nm":[0,1,1],"db10Fu8m":[1,0,0],"HJaKfIom":[1,0,0],"f7yfEllm":[1,0,0],"bX2JnAOm":[1,0,0],"GvZ3b3Ym":[1,0,0],"inFKtRPm":[1,0,0],"SbsdS1fm":[0,1,0],"063FqgEm":[0,1,0],"0KV3NGWm":[0,1,0],"r9EurX3m":[0,1,0],"NB9MPzEm":[0,1,0],"LZWiHdSm":[0,1,0],"3pvfIxgm":[0,1,0],"U4p6LcYm":[0,1,0],"DNStmrKm":[0,1,0],"EZmvdq7m":[0,1,0],"upEWWnpm":[0,1,0],"ly65e96m":[0,1,0]},"NEEDLE":{"xQmCkhAm":[1,0,0],"xEut5NNm":[1,0,0],"GvZ6jUHm":[1,0,0],"tk2mKOOm":[1,0,0],"IuVYq0Wm":[1,0,0],"TQ7yVVpm":[1,0,0],"VPHi2h4m":[0,1,1],"w6xGoELm":[0,1,1],"aYc9b72m":[0,1,1],"E47DwJVm":[0,1,1],"ephPxsSm":[0,1,1],"kVb7Q4Bm":[0,1,1],"CkyQdzXm":[0,1,0],"aU1AYapm":[0,1,0],"1GXnlnLm":[0,1,0],"PDnSa0em":[0,1,0],"ntncllNm":[0,1,0],"XeGdlMMm":[0,1,0]},"WRITING":{"Rn44kyMm":[0,1,1],"s6aItcQm":[0,1,1],"RxbrdD2m":[0,1,1],"JjEmguKm":[0,1,1],"usGqVhxm":[0,1,1],"ZrU22hVm":[0,1,1],"XvmrP4nm":[0,1,1],"XpLLmLom":[0,1,1],"T5AA5YUm":[0,1,1],"0ks8x4Fm":[1,0,0],"5YY0KL4m":[1,0,0],"XBnngoAm":[1,0,0],"sFB28p9m":[1,0,0],"rMEJJKwm":[1,0,0],"i84CESYm":[1,0,0],"RenCMIXm":[1,0,0],"xmOmfycm":[1,0,0],"YmEZPORm":[1,0,0],"fHyeqe8m":[0,1,0],"Z2kNoPem":[0,1,0],"3oIPmAvm":[0,1,0],"2C6GxoOm":[0,1,0],"YsRDCHpm":[0,1,0],"U2bleuLm":[0,1,0],"8NhgLTbm":[0,1,0]},"SCREW":{"SMPSwK4m":[1,0,0],"TzfnpYWm":[1,0,0],"KFQC2uTm":[1,0,0],"CQdzmxkm":[1,0,0],"4lG5vbem":[1,0,0],"0LoHpFfm":[1,0,0],"9f1iYWEm":[0,1,1],"QJeVC67m":[0,1,1],"ywR4M71m":[0,1,1],"3zd8IxUm":[0,1,1],"I6iOahCm":[0,1,1],"kU78Rvdm":[0,1,1],"LKhyTh0m":[0,1,0],"hcl0nK2m":[0,1,0],"wnsOWxYm":[0,1,0],"4R9wVM9m":[0,1,0],"imuwS48m":[0,1,0],"2lqvestm":[0,1,0]}};
const IMAGE_CATEGORIES = [
    [1, "#Z3859EPGSP8wd7jDaPR9gVG8", "LAKE", "#Rb8b2u7Xh8mmcc5YHTjcs4LE"],
    [2, "#Rb8b2u7Xh8mmcc5YHTjcs4LE", "ISLAND", "#tmSE7mrGAV3CeH5pfk7BmxsM"],
    [3, "#tmSE7mrGAV3CeH5pfk7BmxsM", "BECUNA", "#FTrkdsca73U46YTHQSrgw2Tw"],
    [4, "#FTrkdsca73U46YTHQSrgw2Tw", "SHELL", "#rVZrCyqpyRr4vsVrTJr2N6dc"],
    [5, "#rVZrCyqpyRr4vsVrTJr2N6dc", "BEZOAR", "#FKGuGHGETPkFm9qgJkC4KHxY"],
    [6, "#FKGuGHGETPkFm9qgJkC4KHxY", "TABLE", "#5Mh8BUqmNaZKr2jzTP2qZZeX"],
    [7, "#5Mh8BUqmNaZKr2jzTP2qZZeX", "EGG", "#RExuLy9mYnkbLjx6v4F6K4T6"],
    [8, "#RExuLy9mYnkbLjx6v4F6K4T6", "AGLET", "#uWZ9K4cQSL4kBjGKKfeV2Wxm"],
    [9, "#uWZ9K4cQSL4kBjGKKfeV2Wxm", "NOTEBOOK", "#9vzv57hFGCzvrrRRKs5vSLvH"],
    [10, "#9vzv57hFGCzvrrRRKs5vSLvH", "TRAP", "#XtXjUrJZk5HkExfYH9Q7eCm9"],
    [11, "#XtXjUrJZk5HkExfYH9Q7eCm9", "IRONSAND", "#cUyeaLv385g9r7LyFpY4nhR3"],
    [12, "#cUyeaLv385g9r7LyFpY4nhR3", "WOLF", "#7B7fppEh8tWm2dLaTPjSNLZ7"],
    [13, "#7B7fppEh8tWm2dLaTPjSNLZ7", "ORGAN", "#vwkBNYNMvTXUWx9wyeG5auWh"],
    [14, "#vwkBNYNMvTXUWx9wyeG5auWh", "BONE", "#vbcTKfxMJUrDZCFpgyAhPsdC"],
    [15, "#vbcTKfxMJUrDZCFpgyAhPsdC", "PAN", "#C9gGAhf5ThEqxJ6NBqRN3N44"],
    [16, "#C9gGAhf5ThEqxJ6NBqRN3N44", "RABBIT", "#cXUBTGaJXhLAf4p3WhwthPGG"],
    [17, "#cXUBTGaJXhLAf4p3WhwthPGG", "RANGE", "#x64mmr9W8sjMgnwjhdrFyKuT"],
    [18, "#x64mmr9W8sjMgnwjhdrFyKuT", "SWORD", "#Re4S5mauFqTPLX6MUVTcTPXM"],
    [19, "#Re4S5mauFqTPLX6MUVTcTPXM", "OCTOPUS", "#qJ7yahMuy6uzYSy8tB5xYmUM"],
    [20, "#qJ7yahMuy6uzYSy8tB5xYmUM", "FIRE", "#jQeX2kzy48SkE46BVTJ4zy6T"],
    [21, "#jQeX2kzy48SkE46BVTJ4zy6T", "KNIFE", "#sNwe5mCeHKgLs6e4aU5uVaAG"],
    [22, "#sNwe5mCeHKgLs6e4aU5uVaAG", "ENVELOPE", "#daLYn6KykdxgKBk86pCnPF4W"],
    [23, "#daLYn6KykdxgKBk86pCnPF4W", "RUT", "#4AWTaEwCgn8uycBsJnmKfLZK"],
    [24, "#4AWTaEwCgn8uycBsJnmKfLZK", "WORMWOOD", "#dwpq6e9Xtc2PfsyVL9kT47Wv"],
    [25, "#dwpq6e9Xtc2PfsyVL9kT47Wv", "NEEDLE", "#2q4yJz5qHRuxUX9R4T2qKUw9"],
    [26, "#2q4yJz5qHRuxUX9R4T2qKUw9", "WRITING", "#DuLhMuq8e53LNcNMKrLY7PrJ"],
    [27, "#DuLhMuq8e53LNcNMKrLY7PrJ", "SCREW", "#r9FeWsApx2yC9vYm3uedPJ3P"],
    [28, "#r9FeWsApx2yC9vYm3uedPJ3P", "FINAL", "./puzzle-final-secret-page.htm"],
];

class PuzzleRequest {
  constructor(payload) {
    this.submittedImages = {'selected':[],'unselected':[]}
    this.images = []
    this.success = false
    this.operation = payload['op']
    this.errMsg = ""
    this.key = payload['key'] || this.get_hash_from_index(1)
    this.payload = payload
    this.category = this.get_category_from_key()

    if (this.operation === 1) {
      this.images = this.get_images()
    } else if (this.operation === 2) {
      this.submittedImages = {
        'selected': payload['selected'].split("|").filter(i => i),
        'unselected': payload['unselected'].split("|").filter(i => i),
      }
      this.validate_submission()
    }
  }

  get_category_from_key() {
    // The puzzle will submit a hash as part of its payload; retrieve the matching category from this.
    if (!this.key)
        return this.get_hash_from_index(1)
    const matchingCategory = IMAGE_CATEGORIES.find(c => c[1] === this.key);
    return matchingCategory ? matchingCategory[2] : this.get_hash_from_index(1);
  }

  get_hash_from_index(idx) {
    // Return a category, given an index
    const matchingCategory = IMAGE_CATEGORIES.find(c => c[0] === idx);
    return matchingCategory ? matchingCategory[1] : '';
  }

  get_next_category_from_key() {
    const matchingCategory = IMAGE_CATEGORIES.find(c => c[1] === this.key);
    return matchingCategory ? matchingCategory[3] : '';
  }

  get_images() {
    const images = []
    if (this.category == 'FINAL')
        return images

    // add herrings
    const category_herrings = Object.entries(IMAGE_DATA[this.category]).filter(([k, v]) => v[2]).map(([k, v]) => k);
    images.push(...randomSample(category_herrings, 3))
    // add true positives
    const correct_images = randomInt(3, 5)
    const category_true_positive = Object.entries(IMAGE_DATA[this.category]).filter(([k, v]) => v[0] && !images.includes(k)).map(([k, v]) => k);
    images.push(...randomSample(category_true_positive, correct_images))
    // add incorrect images
    const category_incorrect = Object.entries(IMAGE_DATA[this.category]).filter(([k, v]) => v[1] && !images.includes(k)).map(([k, v]) => k)
    images.push(...randomSample(category_incorrect, IMAGES_REQUIRED - images.length))
    randomShuffle(images);
    return images;
  }

   validate_submission() {
    const images = [
      ...new Set(
        [...this.submittedImages['selected'], ...this.submittedImages['unselected']]
      )
    ];
    if (images.length !== IMAGES_REQUIRED) {
      this.errMsg = "Please try again"
      return
    }

    if (this.submittedImages['selected'].length == 0) {
      this.errMsg = "Please try again"
      return
    }

    // check all selected images are valid
    const submitted_are_valid = this.submittedImages['selected'].every(
      x => Object.entries(IMAGE_DATA[this.category]).some(
        ([k, v]) => x === k && v[0]));
    if (!submitted_are_valid) {
      this.errMsg = "Please try again"
      this.debug = "not all submitted are valid"
      return
    }

    // check that no unselected images are valid
    const unsubmitted_are_valid =
      this.submittedImages['unselected'].some(
        x => Object.entries(IMAGE_DATA[this.category]).some(
          ([k, v]) => x === k && v[0]));
    if (unsubmitted_are_valid) {
      this.errMsg = "Please try again"
      this.debug = "some unsubmitted are valid"
      return
    }

    this.debug = "successful orig_key: " + this.payload['key'] + " key: " + this.key
    this.success = true
  }

  returnResponse() {
    if (this.operation == 1) {
        // This is just getting images
        return [
          this.category,
          this.images, // array of image urls
          this.key // current hash
        ]
    } else if (this.operation == 2) {
      // Validate response
      return [
          this.success ? 1 : 0,
          this.errMsg,
          this.success ? this.get_next_category_from_key() : this.key
      ]
    } else {
      return {
          'op': this.operation,
      }
    }
  }
}

window.stubSend = function(payload, handler) {
  handler(new PuzzleRequest(payload).returnResponse())
};

// Inefficient, but eh, small numbers.
function randomSample(arr, n) {
  if (n > arr.length) throw new Error('invalid n');
  const outputIndices = new Set();
  while (outputIndices.size < n) {
    const newIndex = randomInt(0, arr.length - 1);
    outputIndices.add(newIndex);
  }
  return [...outputIndices].map(i => arr[i]);
}

function randomInt(a, b) {
  return a + Math.floor(Math.random() * (b - a + 1));
}

function randomShuffle(arr) {
  for (let i = 0; i < arr.length - 1; i++) {
    const chosenIndex = randomInt(i, arr.length - 1);
    if (chosenIndex !== i) {
      const temp = arr[chosenIndex];
      arr[chosenIndex] = arr[i];
      arr[i] = temp;
    }
  }
}
