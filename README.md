# automation_us
美国签证自动化录入系统

## 美签系统网页流程图
```flow
st=>start: Start
e=>end
re=>operation: Recovery
sq=>operation: SecureQuestion

info=>subroutine: VisaInfo|current
p1=>operation: Personal1
p2=>operation: Personal2
ap=>operation: AddressPhone
pv=>operation: PptVisa
tl=>operation: Travel
tc=>operation: TravelCompanions
put=>operation: PreviousUSTravel
uc=>operation: USContact
rt=>operation: Relatives
sp=>operation: Spouse
w1=>operation: WorkEducation1
w2=>operation: WorkEducation2
w3=>operation: WorkEducation3
sb1=>operation: SecurityandBackground1
sb2=>operation: SecurityandBackground2
sb3=>operation: SecurityandBackground3
sb4=>operation: SecurityandBackground4
sb5=>operation: SecurityandBackground5

po=>subroutine: Photo|current
up=>operation: UploadPhoto
cp=>operation: ConfirmPhoto

rw=>subroutine: Review|current
sc=>subroutine: SignCertify|current
done=>subroutine: Done|current


cond=>condition: Have AAcode?
cond1=>condition: 是否填完?
cond2=>condition: 上传完成?
cond2=>condition: 审查完成?


st->cond
cond(yes)->re->info->cond1
cond(no)->sq->info->cond1
cond1(yes)->po->cond2
cond1(no)->
p1->p2->ap->pv->tl->tc->put->uc->rt->sp->w1->w2->w3->sb1->sb2->sb3->sb4->sb5->cond1
cond2(yes)->sc->cond3
cond2(no)->up->cp->cond2

```