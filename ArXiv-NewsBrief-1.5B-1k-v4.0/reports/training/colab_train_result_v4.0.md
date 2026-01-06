======================================================================
🚀 ArXiv-NewsBrief - 완전판
======================================================================

🎯 실행 모드: 전체 (Full)
📦 모델: ArXiv-NewsBrief-1.5B-1k-v4.0
📊 데이터: 1000개
🔄 에포크: 5
🧪 테스트: 3개

✅ 후처리 함수 로드 완료

======================================================================
📦 STEP 1: 패키지 설치
======================================================================

🔧 bitsandbytes 설치...
📥 나머지 패키지...
✅ 패키지 설치 완료!

======================================================================
📚 STEP 2: 라이브러리 Import
======================================================================
✅ Import 완료

🔍 GPU 환경 확인...
✅ GPU: NVIDIA A100-SXM4-80GB
✅ 메모리: 85.17GB
✅ bitsandbytes: 0.49.0

💾 Google Drive 마운트...
✅ 마운트 완료

⚙️ 설정 요약:
  모드: 전체 (Full)
  모델: ArXiv-NewsBrief-1.5B-1k-v4.0
  베이스: Qwen/Qwen2.5-1.5B-Instruct
  데이터: v4_training_data_all.csv
  샘플 수: 1000개
  에포크: 5
  저장 위치: /content/drive/MyDrive/ArXiv-Models/ArXiv-NewsBrief-1.5B-1k-v4.0

======================================================================
📂 STEP 3: 데이터 로드 및 준비
======================================================================
📥 데이터 로딩: v4_training_data_all.csv
✅ 전체 데이터: 782개
✅ 성공 데이터: 782개
✅ V4 필터: 782개

📊 최종 데이터: 782개

📊 데이터 분할:
  Train: 704개 (90.0%)
  Val: 78개 (10.0%)

📊 데이터 통계:
  평균 단어: 52.1
  45단어 이하: 89/704 (12.6%)
  평균 문장: 2.0
  2문장: 696/704 (98.9%)

📝 데이터 샘플 (1/704):
======================================================================
📖 초록:
we present an analysis of the two - point angular correlation function of the elais s1 survey. the survey covers 4 deg and contains 462 sources detected at 15 m to a 5 flux limit of 0.45 mjy. using th...

✨ V4 요약:
This study looked at how galaxies are spread out in the sky using infrared light, finding that they tend to cluster together, but not as much as galaxies seen with regular light. This suggests that galaxies identified by their infrared glow are less grouped than those seen in visible light, especially at greater distances.

📊 54단어, 2문장
======================================================================

======================================================================
📝 STEP 4: 프롬프트 생성
======================================================================
✅ 토크나이저 로드

✨ 시스템 프롬프트:
"Summarize the following text in simple, clear English that anyone can understand. Use no more than two complete sentences."

🔄 프롬프트 적용 중...
Map: 100%
 704/704 [00:00<00:00, 6869.75 examples/s]
Map: 100%
 78/78 [00:00<00:00, 3382.05 examples/s]
✅ 완료

======================================================================
🔤 STEP 5: 토크나이즈 (텍스트→숫자)
======================================================================
🔄 토크나이즈 중...
Map: 100%
 704/704 [00:00<00:00, 918.13 examples/s]
Map: 100%
 78/78 [00:00<00:00, 779.68 examples/s]
✅ 완료

======================================================================
🚀 STEP 6: 모델 로딩 (4-bit 양자화)
======================================================================
📥 Qwen/Qwen2.5-1.5B-Instruct 로딩 중...
✅ 모델 로드 완료

🔧 LoRA 어댑터 설정...

📊 학습 파라미터:
  학습 가능: 4,358,144 (0.49%)
  전체: 892,974,592

======================================================================
🏋️ STEP 7: 모델 학습 (5 에포크)
======================================================================

📊 학습 정보:
  모드: 전체 (Full)
  데이터: 704개
  에포크: 5
  총 스텝: ~880
  예상 시간: ~44분
======================================================================
/usr/local/lib/python3.12/dist-packages/torch/_dynamo/eval_frame.py:1044: UserWarning: torch.utils.checkpoint: the use_reentrant parameter should be passed explicitly. Starting in PyTorch 2.9, calling checkpoint without use_reentrant will raise an exception. use_reentrant=False is recommended, but if you need to preserve the current default behavior, you can pass use_reentrant=True. Refer to docs for more details on the differences between the two variants.
  return fn(*args, **kwargs)
 [880/880 29:38, Epoch 5/5]
Step	Training Loss	Validation Loss
50	2.179600	2.099127
100	2.081200	2.028833
150	2.139100	2.013743
200	1.982800	2.003889
250	1.997700	1.999719
300	1.989200	1.995565
350	1.927800	1.990512
400	1.904400	1.996075
450	1.810900	1.996067
500	1.901800	1.995227
550	1.834800	2.010142
600	1.911700	2.011550
650	1.843400	2.012139
700	1.825300	2.011491
750	1.728800	2.027000
800	1.679400	2.033656
850	1.738000	2.032377
/usr/local/lib/python3.12/dist-packages/torch/_dynamo/eval_frame.py:1044: UserWarning: torch.utils.checkpoint: the use_reentrant parameter should be passed explicitly. Starting in PyTorch 2.9, calling checkpoint without use_reentrant will raise an exception. use_reentrant=False is recommended, but if you need to preserve the current default behavior, you can pass use_reentrant=True. Refer to docs for more details on the differences between the two variants.
  return fn(*args, **kwargs)
/usr/local/lib/python3.12/dist-packages/torch/_dynamo/eval_frame.py:1044: UserWarning: torch.utils.checkpoint: the use_reentrant parameter should be passed explicitly. Starting in PyTorch 2.9, calling checkpoint without use_reentrant will raise an exception. use_reentrant=False is recommended, but if you need to preserve the current default behavior, you can pass use_reentrant=True. Refer to docs for more details on the differences between the two variants.
  return fn(*args, **kwargs)
/usr/local/lib/python3.12/dist-packages/torch/_dynamo/eval_frame.py:1044: UserWarning: torch.utils.checkpoint: the use_reentrant parameter should be passed explicitly. Starting in PyTorch 2.9, calling checkpoint without use_reentrant will raise an exception. use_reentrant=False is recommended, but if you need to preserve the current default behavior, you can pass use_reentrant=True. Refer to docs for more details on the differences between the two variants.
  return fn(*args, **kwargs)
/usr/local/lib/python3.12/dist-packages/torch/_dynamo/eval_frame.py:1044: UserWarning: torch.utils.checkpoint: the use_reentrant parameter should be passed explicitly. Starting in PyTorch 2.9, calling checkpoint without use_reentrant will raise an exception. use_reentrant=False is recommended, but if you need to preserve the current default behavior, you can pass use_reentrant=True. Refer to docs for more details on the differences between the two variants.
  return fn(*args, **kwargs)
/usr/local/lib/python3.12/dist-packages/torch/_dynamo/eval_frame.py:1044: UserWarning: torch.utils.checkpoint: the use_reentrant parameter should be passed explicitly. Starting in PyTorch 2.9, calling checkpoint without use_reentrant will raise an exception. use_reentrant=False is recommended, but if you need to preserve the current default behavior, you can pass use_reentrant=True. Refer to docs for more details on the differences between the two variants.
  return fn(*args, **kwargs)
/usr/local/lib/python3.12/dist-packages/torch/_dynamo/eval_frame.py:1044: UserWarning: torch.utils.checkpoint: the use_reentrant parameter should be passed explicitly. Starting in PyTorch 2.9, calling checkpoint without use_reentrant will raise an exception. use_reentrant=False is recommended, but if you need to preserve the current default behavior, you can pass use_reentrant=True. Refer to docs for more details on the differences between the two variants.
  return fn(*args, **kwargs)
/usr/local/lib/python3.12/dist-packages/torch/_dynamo/eval_frame.py:1044: UserWarning: torch.utils.checkpoint: the use_reentrant parameter should be passed explicitly. Starting in PyTorch 2.9, calling checkpoint without use_reentrant will raise an exception. use_reentrant=False is recommended, but if you need to preserve the current default behavior, you can pass use_reentrant=True. Refer to docs for more details on the differences between the two variants.
  return fn(*args, **kwargs)
/usr/local/lib/python3.12/dist-packages/torch/_dynamo/eval_frame.py:1044: UserWarning: torch.utils.checkpoint: the use_reentrant parameter should be passed explicitly. Starting in PyTorch 2.9, calling checkpoint without use_reentrant will raise an exception. use_reentrant=False is recommended, but if you need to preserve the current default behavior, you can pass use_reentrant=True. Refer to docs for more details on the differences between the two variants.
  return fn(*args, **kwargs)
/usr/local/lib/python3.12/dist-packages/torch/_dynamo/eval_frame.py:1044: UserWarning: torch.utils.checkpoint: the use_reentrant parameter should be passed explicitly. Starting in PyTorch 2.9, calling checkpoint without use_reentrant will raise an exception. use_reentrant=False is recommended, but if you need to preserve the current default behavior, you can pass use_reentrant=True. Refer to docs for more details on the differences between the two variants.
  return fn(*args, **kwargs)
/usr/local/lib/python3.12/dist-packages/torch/_dynamo/eval_frame.py:1044: UserWarning: torch.utils.checkpoint: the use_reentrant parameter should be passed explicitly. Starting in PyTorch 2.9, calling checkpoint without use_reentrant will raise an exception. use_reentrant=False is recommended, but if you need to preserve the current default behavior, you can pass use_reentrant=True. Refer to docs for more details on the differences between the two variants.
  return fn(*args, **kwargs)
/usr/local/lib/python3.12/dist-packages/torch/_dynamo/eval_frame.py:1044: UserWarning: torch.utils.checkpoint: the use_reentrant parameter should be passed explicitly. Starting in PyTorch 2.9, calling checkpoint without use_reentrant will raise an exception. use_reentrant=False is recommended, but if you need to preserve the current default behavior, you can pass use_reentrant=True. Refer to docs for more details on the differences between the two variants.
  return fn(*args, **kwargs)
/usr/local/lib/python3.12/dist-packages/torch/_dynamo/eval_frame.py:1044: UserWarning: torch.utils.checkpoint: the use_reentrant parameter should be passed explicitly. Starting in PyTorch 2.9, calling checkpoint without use_reentrant will raise an exception. use_reentrant=False is recommended, but if you need to preserve the current default behavior, you can pass use_reentrant=True. Refer to docs for more details on the differences between the two variants.
  return fn(*args, **kwargs)
/usr/local/lib/python3.12/dist-packages/torch/_dynamo/eval_frame.py:1044: UserWarning: torch.utils.checkpoint: the use_reentrant parameter should be passed explicitly. Starting in PyTorch 2.9, calling checkpoint without use_reentrant will raise an exception. use_reentrant=False is recommended, but if you need to preserve the current default behavior, you can pass use_reentrant=True. Refer to docs for more details on the differences between the two variants.
  return fn(*args, **kwargs)
/usr/local/lib/python3.12/dist-packages/torch/_dynamo/eval_frame.py:1044: UserWarning: torch.utils.checkpoint: the use_reentrant parameter should be passed explicitly. Starting in PyTorch 2.9, calling checkpoint without use_reentrant will raise an exception. use_reentrant=False is recommended, but if you need to preserve the current default behavior, you can pass use_reentrant=True. Refer to docs for more details on the differences between the two variants.
  return fn(*args, **kwargs)
/usr/local/lib/python3.12/dist-packages/torch/_dynamo/eval_frame.py:1044: UserWarning: torch.utils.checkpoint: the use_reentrant parameter should be passed explicitly. Starting in PyTorch 2.9, calling checkpoint without use_reentrant will raise an exception. use_reentrant=False is recommended, but if you need to preserve the current default behavior, you can pass use_reentrant=True. Refer to docs for more details on the differences between the two variants.
  return fn(*args, **kwargs)
/usr/local/lib/python3.12/dist-packages/torch/_dynamo/eval_frame.py:1044: UserWarning: torch.utils.checkpoint: the use_reentrant parameter should be passed explicitly. Starting in PyTorch 2.9, calling checkpoint without use_reentrant will raise an exception. use_reentrant=False is recommended, but if you need to preserve the current default behavior, you can pass use_reentrant=True. Refer to docs for more details on the differences between the two variants.
  return fn(*args, **kwargs)
/usr/local/lib/python3.12/dist-packages/torch/_dynamo/eval_frame.py:1044: UserWarning: torch.utils.checkpoint: the use_reentrant parameter should be passed explicitly. Starting in PyTorch 2.9, calling checkpoint without use_reentrant will raise an exception. use_reentrant=False is recommended, but if you need to preserve the current default behavior, you can pass use_reentrant=True. Refer to docs for more details on the differences between the two variants.
  return fn(*args, **kwargs)

======================================================================
✅ 학습 완료!
======================================================================
⏱️ 소요 시간: 29.7분
⚡ 평균 속도: 29.7 스텝/분

======================================================================
💾 STEP 8: 모델 저장
======================================================================
✅ 모델 저장: /content/drive/MyDrive/ArXiv-Models/ArXiv-NewsBrief-1.5B-1k-v4.0/final_model
✅ 메타데이터 저장
✅ README 저장

✅ STEP 1-8 완료!

======================================================================
🔬 STEP 9: A/B 테스트 (3개 샘플)
======================================================================

🤖 모델 로딩...
  ✅ 베이스 모델
  ✅ 학습된 모델

📥 테스트 데이터 선택...
  ✅ 3개 선택

🧪 테스트 실행 중...
  1/3... ✅
  2/3... ✅
  3/3... ✅

💾 결과 저장: test_전체_(Full)_20260106_043702.json

======================================================================
📊 결과 분석
======================================================================

베이스 모델: 29.7단어 (3/3 성공)
학습된 모델: 23.0단어 (3/3 성공)

📋 샘플 비교 (1/3):
======================================================================
초록: development of exponentially scaling methods has seen great progress in tackling larger systems than previously thought possible. one such technique ,...

목표: Scientists have developed a new, faster way to solve complex quantum chemistry problems that were previously too difficult for computers. This improved method allows for accurate calculations on larger systems, like the chromium dimer, in a fraction of the time compared to older techniques, and can also efficiently calculate excited state energies.

베이스: Exponential growth of computational complexity means only very large molecular systems have been feasible before. Researchers developed algorithms capable of handling bigger systems thanks to their ability to sample determinant combinations randomly rather than exhaustively calculate all possibilities.
학습: Scientists have developed faster computer algorithms—like Full Configuration Interaction Quantum Monte Carlo—to solve complex molecular problems that were too hard before.
======================================================================

======================================================================
✅ 전체 파이프라인 완료!
======================================================================

📁 저장 위치:
  모델: /content/drive/MyDrive/ArXiv-Models/ArXiv-NewsBrief-1.5B-1k-v4.0/final_model
  결과: /content/drive/MyDrive/ArXiv-Models/ArXiv-NewsBrief-1.5B-1k-v4.0/results/test_전체_(Full)_20260106_043702.json

======================================================================
🎉 프로그램 종료
======================================================================