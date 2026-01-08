[AI 휴먼] 조화평
chopeace
Invisible

[AI 휴먼] 조화평 — 1:02 PM
"학습의 정답데이터" 는 무엇을 말하는지요? 이부분은 회의떄 예기를 하면 될듯해요. 더 빠를듯해요 채팅보다
LLM Teacher를 말씀하는지등?
@[AI휴먼] 고형규 저는회의 하고 진행해도 되고요
[AI휴먼] 고형규 — 1:05 PM
다른분들은 회의하실수있나요...?
[AI 휴먼] 조화평 — 1:05 PM
예 그럼 지금봐요
[AI휴먼] 박진서 — 1:05 PM
저는 가능합니다.
[AI휴먼] 고형규 — 1:06 PM
@[AI휴먼] 신혜리 혜리님 혹시 회의 참여 어려우시면 채팅으로라도 참석 가능하실까요..?
[AI휴먼] 신혜리 — 1:07 PM
아 가능합니다
잠시만요
[AI 휴먼] 조화평 — 1:09 PM
리포트도 수정됬습니다. ㅍ
https://github.com/chopeacekr/my-news-briefing/blob/main/ArXiv-NewsBrief-1.5B-1k-v4.0/reports/REPORT.md
GitHub
my-news-briefing/ArXiv-NewsBrief-1.5B-1k-v4.0/reports/REPORT.md at ...
news briefing in tts. Contribute to chopeacekr/my-news-briefing development by creating an account on GitHub.
my-news-briefing/ArXiv-NewsBrief-1.5B-1k-v4.0/reports/REPORT.md at ...
[AI휴먼] 박진서 — 1:45 PM
그 개발자 모드 한다는게 데이터셋 생성기 그쪽인가요?
[AI휴먼] 고형규 — 1:45 PM
고형규 , 박진서님 - ArXiv-NewsBrief-1.5B-1k-v4.0 코드 개발자 모드 혹은 디버그 모드 형식으로 각 단계별 소요시간 및 성능 확인
신혜리님 - ArXiv-NewsBrief-1.5B-1k-v4.0 코드 내의 prompt 향상시도
조화평님 - 웹개발 진행
진서님만 보이스 챗 참여가능하실까요??
[AI휴먼] 박진서 — 1:46 PM
네
[AI휴먼] 고형규 — 1:50 PM
저가 좀 급한 마음에 역할 분담 과정을 빠르게 넘어간것같아서
의문이나 기억이 안나시는 부분 있으시면 언제든 편하게 연락주세요 ! 
[AI휴먼] 박진서 — 1:52 PM
그 학습 과정같은건 최소치로 잡고 하는게 낫겟죠?
[AI휴먼] 고형규 — 1:55 PM
원본 그대로 해주시는게 가장 좋을것같긴 합니다 !
하지만 오늘 마무리시간에 각자의 결과로 조율하면 되니까
지금은 진서님 편하신 방법으로 해주시면되겠습니다 !
[AI 휴먼] 조화평 — 2:00 PM
다시 정리하자면 이부분은 dataset_generator.py 이진행합니다.
Image
[AI휴먼] 박진서 — 2:00 PM
일단 스텝별로 분리하였고,  실행 테스트까지 해볼게요
[AI휴먼] 고형규 — 2:00 PM
넵 !
[AI휴먼] 박진서 — 2:01 PM
이게 하나로 붙어있음 되는데 불리시 안되는 경우가 있어서
[AI 휴먼] 조화평 — 2:02 PM
이부분은 sft_train_data.py 진행합니다.
Image
이 코드에 v2버전으로 추론기능 추가했구요.
sft_merge.py  --> SFT 에서 BASE로 동결해서 병합하는 코드입니다.
sft_verify_merge.py -> 병합된 폴더로부터 읽어서 하나씩 추론하는 코드입니다.; 병합(merged) 경로: /content/drive/MyDrive/ArXiv-Models/ArXiv-NewsBrief-1.5B-1k-v4.0/merged_model
이런식으로.
Image
여기까지 혹시나 이해했으면 확인하고자 하니 답변부탁드립니다. 못하셨으면 질문해주세요
[AI휴먼] 박진서 — 2:15 PM
분리시  제대로 작동하는거 확인하였고, 각 셀당 실핼 시간도 따로 저장해둘까요?
[AI휴먼] 고형규 — 2:16 PM
네 ! 그래주시면 감사하겠습니다 !
[AI휴먼] 박진서 — 2:33 PM
일단 셀 분리한거 실행시간이랑  사용 메모리 최고점과 최저점 적어놧습니다.
V4.0_SFT_DATASET_maker

총 셀 : 14개.

1번셀 : 0초(설정)
2번셀: 19초(패키지 설치)
Expand
V4.0_SFT_DATASET_maker 실행 시간.txt
1 KB
[AI휴먼] 신혜리 — 2:36 PM
저도 아까 셀 분리해서,  Prompt 만 변경 해서 샘플 데이터 3개씩 계속 변경 해봤는데, 훨씬 낫네요
지금 최종 변경한 Prompt로 공유 드릴게요. 이걸로 좀 더 큰 사이즈 진서님이 공유계정으로 한번 생성해봐 주셔도 괜찮을거 같습니다. 데이터 요약 학습 및 생성 자체는 A100으로 하면 엄청 빨리 될 듯 하니
샘플 최종 뽑은거 한번 보여 드릴게요
잠시만요
[AI 휴먼] 조화평 — 2:39 PM
혹시 제가 100개 추론한거 않드렸나요?
어디에 올렸는데 몰라서요
[AI휴먼] 신혜리 — 2:40 PM
지금 드리는 학습데이터 샘플에서 괄호는 따옴표입니다. ( 말로 읽었을 때, 문장 문법 틀리지 않다는 뜻)
index,article,original_abstract,original_words,original_sentences,llm_summary,llm_words,llm_sentences,llm_mode,llm_name,llm_model,llm_success,llm_version,group_id,test_mode,created_at
2000,"in classical statistics , it is often assumed that the outcome of an experiment is precise and the uncertainty of observations is solely due to randomness. under this assumption ,. numerical data are represented as collections of real numbers. in recent years , however , there has been increased interest in situations when exact outcomes of the experiment are very difficult or impossible to obtain , or to measure. the imprecise nature of the data thus collected is caused by various factors such as measurement errors , computational errors , loss or lack of information. under such circumstances and , in general , any other circumstances such as grouping and censoring ,. when observations can not be pinned down to single numbers , data are better represented by intervals. practical examples include interval - valued stock prices , oil prices , temperature data , medical records , mechanical measurements , among many others. in the statistical literature ,. random intervals are most often studied in the framework of random sets , for which the probability - based theory has developed since the publication of the seminal book matheron ( 1975 ). studies on the corresponding statistical methods to analyze set - valued data , while still at the early stage , have shown promising advances. see stoyan ( 1998 ) for a comprehensive review. specifically , to analyze interval - valued data , the earliest attempt probably dates back to 1990 , when diamond published","many statistical data are imprecise due to factors such as measurement errors , computation errors , and lack of information. in such cases , data are better represented by intervals rather than by single numbers. existing methods for analyzing interval - valued data include regressions in the metric space of intervals and symbolic data analysis , the latter being proposed in a more general setting. however , there has been a lack of literature on the parametric modeling and distribution - based inferences for interval - valued data. in an attempt to fill this gap ,. we extend the concept of normality for random sets by lyashenko and propose a normal hierarchical model for random intervals. in addition. , we develop a minimum contrast estimator ( mce ) for the model parameters , which we show is both consistent and asymptotically normal. simulation studies support our theoretical findings , and show very promising results. finally , we successfully apply our model and mce to a real dataset .",168,10,"Many datasets contain imprecise information, so representing data as ranges—rather than single numbers—is often more accurate. This research introduces a new statistical model and estimation method to better analyze these range-based datasets, demonstrating its effectiveness through simulations and a real-world example.",41,2,1,Google Gemini,models/gemma-3-27b-it,True,V4,0,True,2026-01-08T05:34:33.301983
2001,"a beguiling prediction of an expanding universe is that distant objects will appear to age at a slower rate than nearby ones. type ia supernovae ( sne ia ) provide extragalactic clocks of unparalleled precision which are sufficiently luminous to reveal this remarkable phenomenon. while a few doubt that expansion alone causes cosmological redshifts ( e.g. , arp 1987 , 1994 ; arp et al. 1990 ; narlikar & arp 1993 ) , the conventional interpretation has only modest experimental verification ( sandage & perelmuter 1991 ). initial suggestions that time dilation might be seen in the photometric history of sne ia ( wilson 1939 ; rust 1974 ) have been confirmed with recent observations of high redshift sn ia light curves ( leibundgut et al. 1996 ; goldhaber et al. specifically , leibundgut et al. (. 1996 ) demonstrated that the broad light curve of sn ia 1995k ( z=0.479 ) was consistent with those of nearby sne ia when dilated by a factor ( 1+z ) as prescribed by cosmological expansion. yet. recent work has shown that there is an intrinsic variation in the breadth of sn ia light curves which is related to the peak luminosity of the supernova ( phillips 1993 ; riess , press , & kirshner 1995 , 1996 ; hamuy et al. 1995 , 1996a , b ). the sense of the correlation is that more luminous sne ia give rise to broader light curves. a skeptic might postulate that within the large volume searched at high redshift , we are naturally selecting the intrinsically bri","we have developed a quantitative , empirical method for estimating the age of type ia supernovae ( sne ia ) from a single spectral epoch. the technique examines the goodness of fit of spectral features as a function of the temporal evolution of a large database of sne ia spectral features. when a sn ia spectrum with good signal - to - noise ratio over the rest frame range 3800 to 6800 is available , the precision of a spectral feature age ( sfa ) is ( 1- ) 1.4 days. sfa estimates are made for two spectral epochs of sn 1996bj ( z=0.574 ) to measure the _ rate _ of aging at high redshift. in the 10.05 days which elapsed between spectral observations ,. sn 1996bj aged 3.35 3.2 days , consistent with the 6.38 days of aging expected in an expanding universe and inconsistent with no time dilation at the 96.4% confidence level. the precision to which individual features constrain the supernova age has implications for the source of inhomogeneities among sne ia .",177,14,"Researchers have created a new way to accurately determine how old a specific type of exploding star (Type Ia supernova) is by analyzing its light spectrum. Using this method on a distant supernova, they found evidence supporting the idea that the universe is expanding, and this expansion causes time to pass differently at great distances.",55,2,1,Google Gemini,models/gemma-3-27b-it,True,V4,0,True,2026-01-08T05:34:43.335367
2002,"heegaard floer theory is a set of invariants for closed , connected 3-manifolds and cobordisms between them , with a related invariant for closed 4-manifolds. together these invariants form a dimensional topological quantum field theory ( tqft ) , meaning a functor from the cobordism category of 3-manifolds to , in this case , the category of graded abelian groups. + the construction of heegaard floer homology involves counting holomorphic curves associated to heegaard diagrams of 3-manifolds. specifically , given a 3-manifold with a genus heegaard diagram , the invariant is defined as the homology of a chain complex generated by g - tuples of intersection points between the and curves. in lipshitz reformulation , the differential arises from counts of rigid holomorphic curves in the symplectic manifold. \times $ ] , with boundaries mapping to the lagrangian submanifolds and. the maps associated to cobordisms arise from a similar construction , which uses heegaard triples to represent certain elementary cobordisms. + in 2008 , lipshitz , ozsvth and thurston developed bordered heegaard floer homology , which generalizes to parametrized riemann surfaces and to bordered 3-manifolds , meaning 3-manifolds with parametrized boundary. given two such 3-manifolds and , if the surfaces and have compatible p","lipshitz , ozsvth and thurston defined a bordered heegaard floer invariant for 3-manifolds with two boundary components , including mapping cylinders for surface diffeomorphisms. we define a related invariant for certain 4-dimensional cobordisms with corners , by associating a morphism to each such cobordism between two mapping cylinders and. like the osvth - szab invariants of cobordisms between closed 3-manifolds , this morphism arises from counting holomorphic triangles on heegaard triples. we demonstrate that the homotopy class of the morphism only depends on the symplectic structure of the cobordism in question .",92,4,"Researchers have developed a new mathematical tool to study the shapes of spaces, specifically those with boundaries and corners. This tool analyzes how these spaces connect to each other, and its properties depend on the space’s underlying structure, offering a way to classify them.",44,2,1,Google Gemini,models/gemma-3-27b-it,True,V4,0,True,2026-01-08T05:34:51.001065
v4_training_data_test_ prompt revised.csv
9 KB
제가 Prompt 계속 추가 하면서 3개씩 4번 정도 뽑아본 거고, 중간에 계속 이상한 단어 쓰는 거 없고, 아까 같은 괄호 명사 표기 같은거 나온적 없습니다.
[AI휴먼] 신혜리 — 2:42 PM
안주셨어요~
지금 근데 새로 학습 데이터 새로 바꾸는 시점이니까 혹시 다시 실행 하셔야 하는 상황이면 우선 인퍼런스 당장 다시 안하셔도 될거 같습니다.
[AI 휴먼] 조화평 — 2:44 PM
이런실수를
[AI휴먼] 신혜리 — 2:44 PM
학습데이터 생성 프롬프트 변경 

USER_PROMPT_V4 = """Summarize the following text in simple, clear English that anyone can understand. Make it as for the script not for reading. Use no more than two complete sentences. Do not include my prompt message in result. Make sure to keep still professional tone and wording. 
[AI휴먼] 박진서 — 2:45 PM
어 그 뭐냐 제가 뭐 따로 해야할게 있다하지 않앗나요?
[AI 휴먼] 조화평 — 2:45 PM
이미 출력은 남아있으니 보내드립니다.
======================================================================
🔬 STEP 5: 추론 실행 (100개)
======================================================================

🧪 추론 시작...
... (77 KB left)
Expand
message.txt
127 KB
[AI 휴먼] 조화평 — 2:47 PM
문제 ( ) 를 없에기 위함인가? 목적을 알고싶어요. 혹시 이프롬프트로 실행했을떄 결과를 공유 해줄수 있나요?
[AI휴먼] 신혜리 — 2:48 PM
위에 공유 드렸는데요
[AI 휴먼] 조화평 — 2:48 PM
그것였군요 예 확인해볼꼐요
[AI휴먼] 신혜리 — 2:48 PM
아까 말씀 드렸듯이 문제 되었던 부분의 괄호는 3개씩 4번 즉 12번 생성 해본 결과 없었습니다
[AI휴먼] 고형규 — 2:49 PM
저도 확인해보고 의견드리겠습니다 !
[AI 휴먼] 조화평 — 2:49 PM
BEFORE  와  AFTER(이것만 있는데) 필요해요
같은 요약에대한
[AI휴먼] 신혜리 — 2:50 PM
Before 는 이거죠
index,article,original_abstract,original_words,original_sentences,llm_summary,llm_words,llm_sentences,llm_mode,llm_name,llm_model,llm_success,llm_version,group_id,test_mode,created_at
2000,"in classical statistics , it is often assumed that the outcome of an experiment is precise and the uncertainty of observations is solely due to randomness. under this assumption ,. numerical data are represented as collections of real numbers. in recent years , however , there has been increased interest in situations when exact outcomes of the experiment are very difficult or impossible to obtain , or to measure. the imprecise nature of the data thus collected is caused by various factors such as measurement errors , computational errors , loss or lack of information. under such circumstances and , in general , any other circumstances such as grouping and censoring ,. when observations can not be pinned down to single numbers , data are better represented by intervals. practical examples include interval - valued stock prices , oil prices , temperature data , medical records , mechanical measurements , among many others. in the statistical literature ,. random intervals are most often studied in the framework of random sets , for which the probability - based theory has developed since the publication of the seminal book matheron ( 1975 ). studies on the corresponding statistical methods to analyze set - valued data , while still at the early stage , have shown promising advances. see stoyan ( 1998 ) for a comprehensive review. specifically , to analyze interval - valued data , the earliest attempt probably dates back to 1990 , when diamond published","many statistical data are imprecise due to factors such as measurement errors , computation errors , and lack of information. in such cases , data are better represented by intervals rather than by single numbers. existing methods for analyzing interval - valued data include regressions in the metric space of intervals and symbolic data analysis , the latter being proposed in a more general setting. however , there has been a lack of literature on the parametric modeling and distribution - based inferences for interval - valued data. in an attempt to fill this gap ,. we extend the concept of normality for random sets by lyashenko and propose a normal hierarchical model for random intervals. in addition. , we develop a minimum contrast estimator ( mce ) for the model parameters , which we show is both consistent and asymptotically normal. simulation studies support our theoretical findings , and show very promising results. finally , we successfully apply our model and mce to a real dataset .",168,10,"Many datasets aren't perfectly accurate, so representing data as ranges (intervals) instead of single numbers can be more realistic. This research develops a new statistical method to better understand and analyze these interval-based datasets, proving it works well in tests and with real-world examples.",44,2,1,Google Gemini,models/gemma-3-27b-it,True,V4,0,False,2026-01-05T14:21:48.682950
2001,"a beguiling prediction of an expanding universe is that distant objects will appear to age at a slower rate than nearby ones. type ia supernovae ( sne ia ) provide extragalactic clocks of unparalleled precision which are sufficiently luminous to reveal this remarkable phenomenon. while a few doubt that expansion alone causes cosmological redshifts ( e.g. , arp 1987 , 1994 ; arp et al. 1990 ; narlikar & arp 1993 ) , the conventional interpretation has only modest experimental verification ( sandage & perelmuter 1991 ). initial suggestions that time dilation might be seen in the photometric history of sne ia ( wilson 1939 ; rust 1974 ) have been confirmed with recent observations of high redshift sn ia light curves ( leibundgut et al. 1996 ; goldhaber et al. specifically , leibundgut et al. (. 1996 ) demonstrated that the broad light curve of sn ia 1995k ( z=0.479 ) was consistent with those of nearby sne ia when dilated by a factor ( 1+z ) as prescribed by cosmological expansion. yet. recent work has shown that there is an intrinsic variation in the breadth of sn ia light curves which is related to the peak luminosity of the supernova ( phillips 1993 ; riess , press , & kirshner 1995 , 1996 ; hamuy et al. 1995 , 1996a , b ). the sense of the correlation is that more luminous sne ia give rise to broader light curves. a skeptic might postulate that within the large volume searched at high redshift , we are naturally selecting the intrinsically bri","we have developed a quantitative , empirical method for estimating the age of type ia supernovae ( sne ia ) from a single spectral epoch. the technique examines the goodness of fit of spectral features as a function of the temporal evolution of a large database of sne ia spectral features. when a sn ia spectrum with good signal - to - noise ratio over the rest frame range 3800 to 6800 is available , the precision of a spectral feature age ( sfa ) is ( 1- ) 1.4 days. sfa estimates are made for two spectral epochs of sn 1996bj ( z=0.574 ) to measure the _ rate _ of aging at high redshift. in the 10.05 days which elapsed between spectral observations ,. sn 1996bj aged 3.35 3.2 days , consistent with the 6.38 days of aging expected in an expanding universe and inconsistent with no time dilation at the 96.4% confidence level. the precision to which individual features constrain the supernova age has implications for the source of inhomogeneities among sne ia .",177,14,"Scientists have created a new way to accurately determine how old a specific type of exploding star (called a Type Ia supernova) is by analyzing its light spectrum. Using this method on a distant supernova, they found evidence supporting the idea that the universe is expanding, and this expansion causes time to pass differently for objects far away.",58,2,1,Google Gemini,models/gemma-3-27b-it,True,V4,0,False,2026-01-05T14:21:57.581734
2002,"heegaard floer theory is a set of invariants for closed , connected 3-manifolds and cobordisms between them , with a related invariant for closed 4-manifolds. together these invariants form a dimensional topological quantum field theory ( tqft ) , meaning a functor from the cobordism category of 3-manifolds to , in this case , the category of graded abelian groups. + the construction of heegaard floer homology involves counting holomorphic curves associated to heegaard diagrams of 3-manifolds. specifically , given a 3-manifold with a genus heegaard diagram , the invariant is defined as the homology of a chain complex generated by g - tuples of intersection points between the and curves. in lipshitz reformulation , the differential arises from counts of rigid holomorphic curves in the symplectic manifold. \times $ ] , with boundaries mapping to the lagrangian submanifolds and. the maps associated to cobordisms arise from a similar construction , which uses heegaard triples to represent certain elementary cobordisms. + in 2008 , lipshitz , ozsvth and thurston developed bordered heegaard floer homology , which generalizes to parametrized riemann surfaces and to bordered 3-manifolds , meaning 3-manifolds with parametrized boundary. given two such 3-manifolds and , if the surfaces and have compatible p","lipshitz , ozsvth and thurston defined a bordered heegaard floer invariant for 3-manifolds with two boundary components , including mapping cylinders for surface diffeomorphisms. we define a related invariant for certain 4-dimensional cobordisms with corners , by associating a morphism to each such cobordism between two mapping cylinders and. like the osvth - szab invariants of cobordisms between closed 3-manifolds , this morphism arises from counting holomorphic triangles on heegaard triples. we demonstrate that the homotopy class of the morphism only depends on the symplectic structure of the cobordism in question .",92,4,"This research introduces a new mathematical tool to study the shapes of spaces—specifically, 4-dimensional spaces built from 3-dimensional ones. This tool counts specific geometric shapes within these spaces and reveals information about their underlying structure, particularly how they change with different ""symplectic structures.""",43,3,1,Google Gemini,models/gemma-3-27b-it,True,V4,0,False,2026-01-05T14:22:06.509934
2004,"circumstellar disks are created from the remnant material of stellar formation. young protostellar disks provide a method for distinguishing the age of its stellar host and help models converge in determining the exact mechanisms of planet formation. current models suggest most protoplanetary disks will photoevaporate within 1 - 5 myr ( alexander et al 2006a , b ; owen et al. this infancy in which the star has just begun fusion , but not yet shed its disk , is the key time in which planet formation occurs. finding stars within this narrow window of the stars lifetime , provides a further glimpse into the mysterious cause of planet formation. additional clues to planet formation have resulted from the many planetary systems with large dust disks ( kalas et al. 2008 ; lagrange et al. 2010 ; marois et al. 2008 ; 2010 ). the presence of holes , gaps , and azimuthal symmetries in the dust distribution may also indicate the presence of undiscovered planets. although many studies have not found strong correlation between the presence of circumstellar disks and planets , newer _ herschel _ observations have suggested there is a correlation ( marshall et al. 2014 ; kennedy et al. 2014 ; 2015 ). for an alternate view see moro - martn et al. there have been many studies attempting to quantify the occurrence of ir excesses and their inferred disks in fkg and m type stars. the occurrence of excess ir emission at longer wavelengths ( 70","we present sources selected from their wide - field infrared survey explorer ( wise ) colors that merit future observations to image for disks and possible exoplanet companions. introducing a weighted detection method , we eliminated the enormous number of specious excess seen in low signal to noise objects by requiring greater excess for fainter stars. this is achieved by sorting through the 747 million sources of the allwise database. in examining these dim stars. , it can be shown that a non - gaussian distribution best describes the spread around the main - sequence polynomial fit function. using a gamma probability density function ( pdf ). , we can best mimic the main sequence distribution and exclude natural fluctuations in ir excess. with this new methodology we re - discover 25 ir excesses and present 14 new candidates. one source ( j053010.20 - 010140.9 ) , suggests a 8.40 0.73 au disk , a likely candidate for possible direct imagining of planets that are likely fully formed. although all of these sources are well within the current flux ratio limit of ( wyatt 2008 ) , j223423.85 + 403515.8 shows the highest bolometric flux ratio ( =0.0694 ) between disk and host star , providing a very good candidate for direct imaging of the circumstellar disk itself. in re - examining the kepler candidate catalog ( original study preformed by kennedy and wyatt 2012 ). , we found one new candidate that indicates disk like characterist",247,19,"Scientists analyzed data from a large infrared survey of stars to identify those likely surrounded by disks of dust and gas – the kinds of disks where planets form. They found 14 new stars and confirmed 25 previously known stars that are good candidates for further study, potentially even allowing us to directly *see* planets or the disks around them.",60,2,1,Google Gemini,models/gemma-3-27b-it,True,V4,0,False,2026-01-05T14:22:46.771458
2005,"gravitational potential wells that are deep enough to trap gas hotter than can generally be detected in the thermal x - ray emission of the trapped gas. these potential wells range in size from those of massive elliptical galaxies through groups of galaxies to clusters of galaxies. as one proceeds down this sequence , the fraction of the system s baryons that are contained in the virial - temperature gas rises from to. the central cooling time is defined to be the ratio of the central energy density to the central luminosity density due to radiative cooling. in many ,. perhaps most , systems , is shorter than the hubble time. in the case of an elliptical galaxy such as ngc 4472 , , while in a cluster of galaxies such as hydra. hence , we must ask how these systems endure for times that greatly exceed. in the absence of heating , radiative losses cause the central density to rise inexorably as the central temperature falls. the density reaches arbitrarily large values in a time that is slightly shorter than ( murray & balbus , 1992 ). kaiser & binney ( 2003 ) present a semi - analytic model of this process , which ends in a ` cooling catastrophe '. the xmm - newton and chandra satellites have established two facts for which there was sketchy evidence in earlier data. first , although the temperature drops as one approaches the centre of one of these systems , it is boun","cooling flows galaxies : nuclei galaxies : formation galaxies : jets galaxies : luminosity function in cuspy atmospheres , jets driven by supermassive black holes ( bhs ) offset radiative cooling. the jets fire episodically , but often enough that the cuspy atmosphere does not move very far towards a cooling catastrophe in the intervals of jet inactivity. the ability of energy released on the sub - parsec scale of the bh to balance cooling on scales of several tens of kiloparsecs arises through a combination of the temperature sensitivity of the accretion rate and the way in which the radius of jet disruption varies with ambient density. accretion of hot gas does not significantly increase bh masses , which are determined by periods of rapid bh growth and star formation when cold gas is briefly abundant at the galactic centre. hot gas does not accumulate in shallow potential wells. as the universe ages , deeper wells form , and eventually hot gas accumulates. this gas soon prevents the formation of further stars , since jets powered by the bh prevent it from cooling , and it mops up most cold infalling gas before many stars can form. thus bhs set the upper limit to the masses of galaxies. the formation of low - mass galaxies is inhibited by a combination of photo - heating and supernova - driven galactic winds. working in tandem these mechanisms can probably explain the profound difference between the galaxy luminosity function and the mass functi",251,10,"Supermassive black holes in the centers of galaxies release energy in bursts that prevent hot gas from cooling and forming stars, ultimately limiting how large galaxies can grow. This process, along with other factors like radiation and winds, also explains why there are fewer small galaxies than expected in the universe.",51,2,1,Google Gemini,models/gemma-3-27b-it,True,V4,0,False,2026-01-05T14:22:56.382798... (3 MB left)
Expand
v4_training_data_all (1).csv
3 MB
[AI 휴먼] 조화평 — 2:51 PM
같은 초록 원본이면 좋아요.확인해볼게요 감사드려요
[AI휴먼] 신혜리 — 2:52 PM
같은 인덱스에요 2000-2003번까지만 샘플을 해본거니까
내용을 보시지 않아도
저희가 문제 삼는 형식의 이슈 해결 되었으면 되는거라
저는 이정도면 1000개 정도 A100으로 뽑아보는 거 나쁘진 않을 거 같은데, 다른 분들도 확인 해보시고 알려주세요.
[AI 휴먼] 조화평 — 2:56 PM
일단 쳇지피티한데 물어봤어요.
다음 초록에 대한 BEFORE vs AFTER   TTS 로 뉴스브리핑용 요약을 원할시 어떻게 낳은지 분석해줘 영한 번역도 해줘서
in classical statistics , it is often assumed that the outcome of an experiment is precise and the uncertainty of observations is solely due to randomness. under this assumption ,. numerical data are represented as collections of real numbers. in recent years , however , there has been increased interest in situations when exact outcomes of the experiment are very difficult or impossible to obtain , or to measure. the imprecise nature of the data thus collected is caused by various factors such as measurement errors , computational errors , loss or lack of information. under such circumstances and , in general , any other circumstances such as grouping and censoring ,. when observations can not be pinned down to single numbers , data are better represented by intervals. practical examples include interval - valued stock prices , oil prices , temperature data , medical records , mechanical measurements , among many others. in the statistical literature ,. random intervals are most often studied in the framework of random sets , for which the probability - based theory has developed since the publication of the seminal book matheron ( 1975 ). studies on the corresponding statistical methods to analyze set - valued data , while still at the early stage , have shown promising advances. see stoyan ( 1998 ) for a comprehensive review. specifically , to analyze interval - valued data , the earliest attempt probably dates back to 1990 , when diamond published

BEFORE: Many datasets aren't perfectly accurate, so representing data as ranges (intervals) instead of single numbers can be more realistic. This research develops a new statistical method to better understand and analyze these interval-based datasets, proving it works well in tests and with real-world examples.

Expand
message.txt
3 KB
많은 데이터는 완벽하게 정확하지 않기 때문에, 하나의 숫자보다 범위(구간)로 표현하는 것이 더 현실적일 수 있다. 이 연구는 이러한 구간 데이터들을 더 잘 이해하고 분석하기 위한 새로운 통계 방법을 개발했으며, 실험과 실제 사례를 통해 그 효과를 입증했다.
2.많은 데이터에는 부정확한 정보가 포함돼 있어, 하나의 숫자보다 범위로 표현하는 것이 더 정확한 경우가 많다. 이 연구는 이러한 범위 데이터를 분석하기 위한 새로운 통계 모델과 추정 방법을 제시하고, 시뮬레이션과 실제 사례를 통해 그 효과를 보여준다.
곧 마크다운 공유할게요
[AI휴먼] 신혜리 — 3:00 PM
ㅎㅎㅎㅎㅎㅎㅎㅎㅎㅎㅎ
네 더 좋은걸로 하세요.
[AI 휴먼] 조화평 — 3:01 PM
USER_PROMPT_V4 = """Summarize the following text in simple, clear English that anyone can understand. Make it as for the script not for reading. Use no more than two complete sentences. Do not include my prompt message in result. Make sure to keep still professional tone and wording.
# BEFORE vs AFTER 분석  
### 논문 초록 → 뉴스브리핑(TTS) 요약 품질 비교
USER_PROMPT_V4 = """Summarize the following text in simple, clear English that anyone can understand. Make it as for the script not for reading. Use no more than two complete sentences. Do not include my prompt message in result. Make sure to keep still professional tone and wording. 

아래는 **논문 초록을 뉴스브리핑(TTS)용 요약으로 변환할 때**,  
**BEFORE → AFTER가 어떻게 개선되었는지**를 구조·내용·TTS 관점에서 분석한 내용입니다.  
Expand
message.txt
5 KB
중요한 프롬프트 v2 로 결과 git 에 저장해놓겠습니다.
이보다 더 좋은것 있으면 배틀 부탁해요^^
﻿
# BEFORE vs AFTER 분석  
### 논문 초록 → 뉴스브리핑(TTS) 요약 품질 비교
USER_PROMPT_V4 = """Summarize the following text in simple, clear English that anyone can understand. Make it as for the script not for reading. Use no more than two complete sentences. Do not include my prompt message in result. Make sure to keep still professional tone and wording. 

아래는 **논문 초록을 뉴스브리핑(TTS)용 요약으로 변환할 때**,  
**BEFORE → AFTER가 어떻게 개선되었는지**를 구조·내용·TTS 관점에서 분석한 내용입니다.  
(영문 원문 + 한글 번역 포함)

---

## 1️⃣ BEFORE vs AFTER 요약문

### 🔹 BEFORE (기존 요약)

**English**
> Many datasets aren't perfectly accurate, so representing data as ranges (intervals) instead of single numbers can be more realistic. This research develops a new statistical method to better understand and analyze these interval-based datasets, proving it works well in tests and with real-world examples.

**한국어 번역**
> 많은 데이터는 완벽하게 정확하지 않기 때문에, 하나의 숫자보다 범위(구간)로 표현하는 것이 더 현실적일 수 있다. 이 연구는 이러한 구간 데이터들을 더 잘 이해하고 분석하기 위한 새로운 통계 방법을 개발했으며, 실험과 실제 사례를 통해 그 효과를 입증했다.

---

### 🔹 AFTER (개선된 요약, 뉴스브리핑/TTS 최적화)

**English**
> Many datasets contain imprecise information, so representing data as ranges—rather than single numbers—is often more accurate. This research introduces a new statistical model and estimation method to better analyze these range-based datasets, demonstrating its effectiveness through simulations and a real-world example.

**한국어 번역**
> 많은 데이터에는 부정확한 정보가 포함돼 있어, 하나의 숫자보다 범위로 표현하는 것이 더 정확한 경우가 많다. 이 연구는 이러한 범위 데이터를 분석하기 위한 새로운 통계 모델과 추정 방법을 제시하고, 시뮬레이션과 실제 사례를 통해 그 효과를 보여준다.

---

## 2️⃣ BEFORE → AFTER 개선 포인트 분석

### 🧠 ① 일반인 이해도 개선

| 항목 | BEFORE | AFTER |
|----|----|----|
| 문제 설명 | aren't perfectly accurate | **contain imprecise information** |
| 표현 톤 | 교과서적 | **뉴스 브리핑형** |
| 대비 구조 | 약함 | **명확한 대비 표현** |

➡ AFTER는 **왜 숫자 대신 범위를 쓰는지**를 더 직관적으로 설명함

---

### 🧠 ② 초록 충실도 (Faithfulness)

**초록 핵심**
- 데이터는 측정 오차·정보 부족 등으로 부정확
- 단일 숫자보다 구간(interval)이 적합
- 새로운 통계 모델/방법 제안
- 시뮬레이션 + 실제 예제로 검증

| 요소 | BEFORE | AFTER |
|----|----|----|
| 구간 데이터 개념 | ✓ | ✓ |
| 방법 설명 | new statistical method | **model + estimation method** |
| 검증 방식 | tests | **simulations + real example** |

➡ AFTER가 초록 표현에 더 밀착됨

---

### 🧠 ③ TTS(음성 브리핑) 관점 개선

**BEFORE 단점**
- “interval-based datasets” 반복
- 리듬이 다소 평면적

**AFTER 장점**
- “ranges—rather than single numbers—” 대비 구조로 청취 용이
- 뉴스형 동사(introduces, demonstrating) 사용
- 안정적인 문장 리듬

---

### 🧠 ④ 뉴스브리핑 스타일 완성도

| 기준 | BEFORE | AFTER |
|----|----|----|
| 배경 → 기여 구조 | ✓ | ✓ |
| 뉴스 톤 | 보통 | **우수** |
| 전문 용어 밀도 | 낮음 | 낮음 |
| 전달력 | 좋음 | **더 명확** |

---

## 3️⃣ 종합 평가 (LLM Judge 관점)

| 항목 | BEFORE | AFTER |
|----|----|----|
| 일반인 이해도 | 4 / 5 | **5 / 5** |
| 내용 충실도 | 4.5 / 5 | **5 / 5** |
| 유창성 | 4 / 5 | **4.5 / 5** |
| 간결성 | 4.5 / 5 | **4.5 / 5** |
| TTS 적합성 | 보통 | **높음** |

---

## 🎯 결론

AFTER 요약은 **초록의 핵심을 유지하면서도**,  
- 일반인 이해도  
- 뉴스브리핑 톤  
- TTS 전달력  

을 모두 개선한 **고품질 Teacher 요약**에 해당한다.

---

### 📌 확장 가능 작업
- SFT 학습용 Teacher 샘플 포맷화  
- 1문장·12단어 초압축 TTS 버전  
- LLM Judge 자동 채점(JSON) 예시 생성

원하시면 바로 이어서 진행해드릴게요 👍
message.txt
5 KB