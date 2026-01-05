============================================================
🚀 STEP 0.4 V3 - 고품질 학습 (V3 데이터)
============================================================

✅ 후처리 함수 V3 로드 완료

============================================================
📦 STEP 1: 패키지 설치
============================================================

🔧 CUDA 호환 bitsandbytes 설치 중...
📥 나머지 패키지 설치 중...
✅ 패키지 설치 완료!

============================================================
📚 STEP 2: Import 및 초기 설정
============================================================
✅ Import 완료

🔍 GPU 확인...
✅ GPU: NVIDIA A100-SXM4-80GB
✅ 메모리: 79.32 GB

🔍 bitsandbytes 확인...
✅ bitsandbytes 0.49.0

💾 Drive 마운트...
✅ 마운트 완료

⚙️ 설정:
  모델: Qwen2.5-1.5B-Instruct
  버전: V3 (고품질 학습)
  데이터 소스: /content/drive/MyDrive/SummaryDataSet
  데이터 파일: v3_merged_all_data.csv
  데이터 제한: 1000
  출력: /content/drive/MyDrive/arxiv-STEP0.4-V3-FINAL

============================================================
📥 STEP 3: V3 데이터 로드 (SummaryDataSet)
============================================================
📥 데이터 로딩: /content/drive/MyDrive/SummaryDataSet/v3_merged_all_data.csv
✅ 원본 데이터: 1020개
✅ 성공 데이터: 1020개

⚙️ 데이터 제한 적용:
  사용 가능: 1020개
  설정 제한: 1000개
  → 1000개만 사용합니다

📊 데이터 분할:
  사용 가능: 1000개
  Train: 900개 (90.0%)
  Val: 100개 (10.0%)
  총 사용: 1000개

📊 LLM 요약 통계:
  평균 단어: 33.7
  45단어 이하: 898/900 (99.8%)
  평균 문장: 2.1
  2문장: 843/900 (93.7%)

  LLM 분포:
    Google Gemini: 898개 (99.8%)
    GPT-4: 2개 (0.2%)

📋 데이터 예시:
============================================================
원본 초록 (141단어):
  we present an investigation for the generation of intense magnetic fields in dense plasmas with an anisotropic electron fermi - dirac distribution . f...

LLM 요약 (36.0단어, 2.0문장):
  A linear dispersion relation for transverse waves in dense quantum plasmas was used to study intense magnetic field generation. Simulations show magnetic field amplitudes scale with instability growth rate, crucial for understanding laser-solid density plasma experiments.
  (생성: Google Gemini)
============================================================

============================================================
📝 STEP 4: V3 프롬프트 적용
============================================================
/usr/local/lib/python3.12/dist-packages/huggingface_hub/utils/_auth.py:94: UserWarning: 
The secret `HF_TOKEN` does not exist in your Colab secrets.
To authenticate with the Hugging Face Hub, create a token in your settings tab (https://huggingface.co/settings/tokens), set it as secret in your Google Colab and restart your session.
You will be able to reuse this secret in all of your notebooks.
Please note that authentication is recommended but still optional to access public models or datasets.
  warnings.warn(
tokenizer_config.json: 
 7.30k/? [00:00<00:00, 792kB/s]
vocab.json: 
 2.78M/? [00:00<00:00, 71.4MB/s]
merges.txt: 
 1.67M/? [00:00<00:00, 79.5MB/s]
tokenizer.json: 
 7.03M/? [00:00<00:00, 145MB/s]
✅ 토크나이저 로드
🔄 V3 프롬프트 적용 중...
Map: 100%
 900/900 [00:00<00:00, 6762.11 examples/s]
Map: 100%
 100/100 [00:00<00:00, 3778.28 examples/s]
✅ 프롬프트 적용 완료

============================================================
🔤 STEP 5: 토크나이즈
============================================================
🔄 토크나이즈 중...
Map: 100%
 900/900 [00:01<00:00, 738.73 examples/s]
Map: 100%
 100/100 [00:00<00:00, 414.41 examples/s]
✅ 토크나이즈 완료

============================================================
🚀 STEP 6: 모델 로딩 (4-bit)
============================================================
📥 Qwen2.5-1.5B-Instruct 로딩 중...
config.json: 100%
 660/660 [00:00<00:00, 83.2kB/s]
model.safetensors: 100%
 3.09G/3.09G [00:04<00:00, 1.27GB/s]
generation_config.json: 100%
 242/242 [00:00<00:00, 32.3kB/s]
✅ 모델 로드 완료

🔧 LoRA 준비 중...

📊 학습 가능한 파라미터:
trainable params: 4,358,144 || all params: 1,548,072,448 || trainable%: 0.2815

============================================================
🎯 STEP 7: 모델 학습 (V3)
============================================================
`use_cache=True` is incompatible with gradient checkpointing. Setting `use_cache=False`.

🏋️ 학습 시작...
  데이터: 900개 (V3 고품질)
  Epochs: 5
  예상 시간: ~1500분

/usr/local/lib/python3.12/dist-packages/torch/_dynamo/eval_frame.py:1044: UserWarning: torch.utils.checkpoint: the use_reentrant parameter should be passed explicitly. Starting in PyTorch 2.9, calling checkpoint without use_reentrant will raise an exception. use_reentrant=False is recommended, but if you need to preserve the current default behavior, you can pass use_reentrant=True. Refer to docs for more details on the differences between the two variants.
  return fn(*args, **kwargs)
 [1125/1125 38:21, Epoch 5/5]
Step	Training Loss	Validation Loss
50	2.132100	2.052665
100	2.088900	1.995639
150	2.111000	1.984323
200	2.050700	1.974318
250	1.968500	1.969680
300	1.944200	1.966204
350	1.925700	1.964372
400	2.038000	1.962371
450	1.880600	1.959286
500	1.887300	1.968657
550	1.854800	1.967995
600	1.863100	1.968997
650	1.906200	1.963799
700	1.874600	1.981565
750	1.808200	1.983495
800	1.839600	1.984289
850	1.870700	1.984749
900	1.790900	1.985521
950	1.702900	2.003373
1000	1.707000	2.007777
1050	1.810400	2.006570
1100	1.772500	2.007021
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

✅ 학습 완료!

============================================================
💾 STEP 8: 모델 저장
============================================================
✅ 저장 완료: /content/drive/MyDrive/arxiv-STEP0.4-V3-FINAL/final_model

✅ STEP 1-8 완료!

============================================================
🔬 A/B 테스트 (V3)
============================================================

🤖 모델 로딩...
  ✅ 베이스 모델
  ✅ 파인튜닝 모델 (V3)

📥 테스트용 논문 로딩...
  ✅ 3개 논문 로드

🧪 테스트 실행...
  Test 1/3... ✅
  Test 2/3... ✅
  Test 3/3... ✅
✅ 저장: ab_test_v3_20260105_101227.json

============================================================
📊 결과 분석
============================================================

베이스: 39.3단어 (3/3 성공)
  복사 감지: 0건
V3 FT: 37.7단어 (3/3 성공)
  복사 감지: 0건

샘플:

초록 (길이: 1088자):
------------------------------------------------------------
gamma - ray spectra from cosmic - ray proton and electron interactions with dense gas clouds have been calculated using a monte carlo event simulation code , geant4 . such clouds are postulated as a p...
------------------------------------------------------------
LLM 타겟: GEANT4 Monte Carlo simulations modeled gamma-ray spectra from cosmic-ray interactions with dense gas clouds, posited as dark matter. Results constrain low column-density cloud fractions (<10^20 cm^-2) but find models with higher densities (>10^21 cm^-2) remain unconstrained by EGRET data.
------------------------------------------------------------
베이스: The Monte Carlo simulations employing Geant4 predict gamma-ray spectra based on proton-electron interaction within dense gas-clouds, crucial for modeling Baryonic Dark Matter. These predictions contrast favorably with observed EGRET radiation patterns, offering new insights into Milky Way's hidden halo composition.
V3 FT: Monte Carlo simulations modeled cosmic-ray interactions within dense media—postulating them as BDM—to predict γ-ray spectra. Results constrained dark matter fractions up to ~10%, but were nearly unimodal at lower columns due to insufficient data validation.

초록 (길이: 412자):
------------------------------------------------------------
we investigate a hamiltonian lattice version of the two - dimensional wess - zumino model by quantum monte carlo simulations . in order to study the pattern of supersymmetry breaking , we measure the ...
------------------------------------------------------------
LLM 타겟: Quantum Monte Carlo simulations investigated a Hamiltonian lattice Wess-Zumino model to study supersymmetry breaking. Ground state energy measurements proved effective, revealing a correlation length approaching the continuum limit and characterizing the breaking pattern.
------------------------------------------------------------
베이스: The researchers explored the Hamiltonian lattice framework of the Wess-Zumino model using Quantum Monte Carlo methods. They focused on analyzing supersymmetric symmetry breakdown patterns through measurements of both the ground-state energy at low temperatures and the critical correlation lengths during scaling transitions towards thermodynamic equilibrium.
V3 FT: Quantum Monte Carlo simulations analyzed the Wess-Zumino model’s Hamiltonian on lattices via evaluating ground-state energies and correlation lengths. Results demonstrate efficient measurement methods enabling investigation into supersymmetrization breakdown patterns near the continuum limits.

============================================================
✅ A/B 완료!
============================================================

============================================================
✅ 완료!
============================================================

📁 저장 위치:
  모델: /content/drive/MyDrive/arxiv-STEP0.4-V3-FINAL/final_model/
  결과: /content/drive/MyDrive/arxiv-STEP0.4-V3-FINAL/results/ab_test_v3_20260105_101227.json
  데이터: /content/drive/MyDrive/SummaryDataSet/v3_merged_all_data.csv

============================================================
🎉 V3 완료!
============================================================

✨ V3 핵심 개선:
  ✅ 데이터: V3 형식 (llm_summary)
  ✅ 1000개 데이터로 학습
  ✅ 다양한 LLM 생성 요약
  ✅ 자동 데이터 분할

📁 결과: /content/drive/MyDrive/arxiv-STEP0.4-V3-FINAL
📁 데이터: /content/drive/MyDrive/SummaryDataSet/v3_merged_all_data.csv

🚀 V3 완성!
============================================================