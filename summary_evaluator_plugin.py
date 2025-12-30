"""
ArXiv 논문 요약 평가 시스템 (Plugin-Based Architecture)

플러그인 방식으로 설계되어 나중에 LLM 기반 평가로 쉽게 교체 가능합니다.

아키텍처:
1. BaseEvaluator: 추상 베이스 클래스
2. KeywordEvaluator: 현재 키워드 기반 평가 (기본)
3. LLMEvaluator: GPT-4, Claude 등 LLM 평가 (향후)
4. HybridEvaluator: 여러 평가 방식 조합
5. EvaluatorFactory: 평가기 생성 팩토리
6. EvaluatorRegistry: 플러그인 등록 시스템

사용 예시:
    # 방법 1: 기본 평가기 (키워드 기반)
    evaluator = EvaluatorFactory.create("keyword")
    result = evaluator.evaluate(original, generated)
    
    # 방법 2: LLM 평가기 (향후)
    evaluator = EvaluatorFactory.create("gpt4", api_key="...")
    result = evaluator.evaluate(original, generated)
    
    # 방법 3: 하이브리드 (여러 방식 조합)
    evaluator = EvaluatorFactory.create("hybrid", 
                                       evaluators=["keyword", "gpt4"])
    result = evaluator.evaluate(original, generated)
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
import json


# ============================================================
# 1. 평가 결과 표준 포맷
# ============================================================

@dataclass
class EvaluationResult:
    """
    평가 결과 표준 포맷
    
    모든 평가기가 이 형식으로 결과를 반환합니다.
    """
    utility: float  # 유용성 점수 (0-100)
    style: float  # 스타일 점수 (0-100)
    overall: float  # 전체 점수 (0-100)
    details: Dict[str, Any]  # 세부 정보
    metadata: Dict[str, Any]  # 메타데이터 (평가기 이름, 버전 등)
    
    def to_dict(self) -> Dict:
        """딕셔너리로 변환 (하위 호환성)"""
        return {
            "utility": self.utility,
            "style": self.style,
            "overall": self.overall,
            "word_count": self.details.get("word_count", 0),
            "rules": self.details.get("rules", {}),
            "metadata": self.metadata
        }
    
    def to_json(self) -> str:
        """JSON 문자열로 변환"""
        return json.dumps(self.to_dict(), indent=2)


# ============================================================
# 2. 추상 베이스 클래스 (모든 평가기의 인터페이스)
# ============================================================

class BaseEvaluator(ABC):
    """
    평가기 추상 베이스 클래스
    
    모든 평가기는 이 클래스를 상속받아야 합니다.
    새로운 평가 방식을 추가하려면 이 클래스를 상속받으세요!
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Args:
            config: 평가기 설정 딕셔너리
        """
        self.config = config or {}
        self.name = self.__class__.__name__
        self.version = "1.0.0"
    
    @abstractmethod
    def evaluate(self, original: str, generated: str) -> EvaluationResult:
        """
        요약 평가 (추상 메서드)
        
        모든 평가기는 이 메서드를 구현해야 합니다!
        
        Args:
            original: 원본 요약 (목표)
            generated: 생성된 요약
            
        Returns:
            EvaluationResult
        """
        pass
    
    def evaluate_batch(self, pairs: List[Dict[str, str]]) -> List[EvaluationResult]:
        """
        배치 평가 (기본 구현)
        
        필요 시 오버라이드하여 최적화 가능
        """
        results = []
        for pair in pairs:
            result = self.evaluate(pair["original"], pair["generated"])
            results.append(result)
        return results
    
    def get_info(self) -> Dict[str, str]:
        """평가기 정보 반환"""
        return {
            "name": self.name,
            "version": self.version,
            "type": self.__class__.__name__
        }


# ============================================================
# 3. 키워드 기반 평가기 (현재 방식)
# ============================================================

class KeywordEvaluator(BaseEvaluator):
    """
    키워드 기반 평가기
    
    현재 사용 중인 키워드 매칭 + 5가지 규칙 방식
    """
    
    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        
        # 설정 기본값
        self.max_word_count = self.config.get("max_word_count", 50)
        self.word_count_penalty = self.config.get("word_count_penalty", 2)
        self.academic_keywords = self.config.get("academic_keywords", 
            ["novel", "new", "achieve", "improve", "propose", "introduce", "demonstrate"])
        self.subjective_words = self.config.get("subjective_words",
            ["amazing", "wonderful", "terrible", "awesome", "horrible"])
        self.practical_keywords = self.config.get("practical_keywords",
            ["application", "use", "practical", "apply", "implementation"])
    
    def evaluate(self, original: str, generated: str) -> EvaluationResult:
        """키워드 기반 평가"""
        # 유용성 평가
        utility = self._evaluate_utility(original, generated)
        
        # 스타일 평가
        style_result = self._evaluate_style(generated)
        
        # 전체 점수 (가중 평균)
        overall = (utility * 0.5 + style_result["overall"] * 0.5)
        
        return EvaluationResult(
            utility=utility,
            style=style_result["overall"],
            overall=overall,
            details={
                "word_count": len(generated.split()),
                "rules": style_result["rules"]
            },
            metadata={
                "evaluator": self.name,
                "version": self.version,
                "method": "keyword_based"
            }
        )
    
    def _evaluate_utility(self, original: str, generated: str) -> float:
        """유용성 평가 (키워드 매칭)"""
        orig_words = set(original.lower().split())
        gen_words = set(generated.lower().split())
        
        if len(orig_words) == 0:
            return 0.0
        
        common = orig_words & gen_words
        score = len(common) / len(orig_words) * 100
        return min(100.0, score)
    
    def _evaluate_style(self, generated: str) -> Dict:
        """스타일 평가 (5가지 규칙)"""
        rule1 = self._rule1_word_count(generated)
        rule2 = self._rule2_academic_keywords(generated)
        rule3 = self._rule3_technical_terms(generated)
        rule4 = self._rule4_no_subjective(generated)
        rule5 = self._rule5_practical_mention(generated)
        
        overall = (rule1 + rule2 + rule3 + rule4 + rule5) / 5
        
        return {
            "overall": overall,
            "rules": {
                "rule1": rule1,
                "rule2": rule2,
                "rule3": rule3,
                "rule4": rule4,
                "rule5": rule5
            }
        }
    
    def _rule1_word_count(self, generated: str) -> float:
        word_count = len(generated.split())
        if word_count <= self.max_word_count:
            return 100.0
        excess = word_count - self.max_word_count
        return float(max(0, 100 - excess * self.word_count_penalty))
    
    def _rule2_academic_keywords(self, generated: str) -> float:
        text_lower = generated.lower()
        for keyword in self.academic_keywords:
            if keyword in text_lower:
                return 100.0
        return 50.0
    
    def _rule3_technical_terms(self, generated: str) -> float:
        words = generated.split()
        tech_terms = [w for w in words if w and (w[0].isupper() or len(w) >= 15)]
        count = len(tech_terms)
        
        if count >= 4:
            return 100.0
        elif count >= 2:
            return 75.0
        else:
            return float(count * 25)
    
    def _rule4_no_subjective(self, generated: str) -> float:
        text_lower = generated.lower()
        for word in self.subjective_words:
            if word in text_lower:
                return 50.0
        return 100.0
    
    def _rule5_practical_mention(self, generated: str) -> float:
        text_lower = generated.lower()
        for keyword in self.practical_keywords:
            if keyword in text_lower:
                return 100.0
        return 50.0


# ============================================================
# 4. LLM 기반 평가기 (향후 구현)
# ============================================================

class LLMEvaluator(BaseEvaluator):
    """
    LLM 기반 평가기 (GPT-4, Claude 등)
    
    향후 구현: OpenAI API, Anthropic API 등을 사용한 평가
    
    사용 예시:
        evaluator = LLMEvaluator(config={
            "provider": "openai",  # or "anthropic"
            "model": "gpt-4",
            "api_key": "sk-..."
        })
    """
    
    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        
        self.provider = self.config.get("provider", "openai")
        self.model = self.config.get("model", "gpt-4")
        self.api_key = self.config.get("api_key")
        
        # API 클라이언트 초기화 (향후 구현)
        # self.client = self._init_client()
    
    def evaluate(self, original: str, generated: str) -> EvaluationResult:
        """
        LLM을 사용한 평가
        
        향후 구현:
        1. LLM에게 원본과 생성된 요약 전달
        2. 유용성, 스타일 점수 요청
        3. 결과 파싱 및 반환
        """
        # 임시 구현 (실제로는 API 호출)
        # return self._call_llm_api(original, generated)
        
        # 현재는 키워드 평가로 fallback
        print(f"⚠️ LLM 평가 ({self.provider}/{self.model})는 아직 구현되지 않았습니다.")
        print(f"   → KeywordEvaluator로 fallback")
        
        fallback = KeywordEvaluator(self.config)
        result = fallback.evaluate(original, generated)
        result.metadata["evaluator"] = f"LLMEvaluator (fallback)"
        return result
    
    def _call_llm_api(self, original: str, generated: str) -> EvaluationResult:
        """
        LLM API 호출 (향후 구현)
        
        구현 예시:
        
        if self.provider == "openai":
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[{
                    "role": "system",
                    "content": "You are an expert evaluator..."
                }, {
                    "role": "user",
                    "content": f"Original: {original}\\nGenerated: {generated}"
                }]
            )
            # 파싱 및 점수 추출
        
        elif self.provider == "anthropic":
            response = anthropic.messages.create(
                model=self.model,
                messages=[...]
            )
            # 파싱 및 점수 추출
        """
        raise NotImplementedError("LLM API 호출은 아직 구현되지 않았습니다.")


# ============================================================
# 5. 하이브리드 평가기 (여러 방식 조합)
# ============================================================

class HybridEvaluator(BaseEvaluator):
    """
    하이브리드 평가기 (여러 평가 방식 조합)
    
    여러 평가기의 결과를 가중 평균하여 최종 점수 산출
    
    사용 예시:
        evaluator = HybridEvaluator(config={
            "evaluators": [
                {"type": "keyword", "weight": 0.5},
                {"type": "gpt4", "weight": 0.5, "api_key": "..."}
            ]
        })
    """
    
    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        
        # 평가기 리스트
        self.evaluators = []
        self.weights = []
        
        # 설정에서 평가기 생성
        evaluator_configs = self.config.get("evaluators", [])
        for eval_config in evaluator_configs:
            eval_type = eval_config.get("type", "keyword")
            weight = eval_config.get("weight", 1.0)
            
            evaluator = EvaluatorFactory.create(eval_type, eval_config)
            self.evaluators.append(evaluator)
            self.weights.append(weight)
        
        # 가중치 정규화
        total_weight = sum(self.weights)
        self.weights = [w / total_weight for w in self.weights]
    
    def evaluate(self, original: str, generated: str) -> EvaluationResult:
        """여러 평가기 결과를 가중 평균"""
        results = []
        
        # 각 평가기 실행
        for evaluator in self.evaluators:
            result = evaluator.evaluate(original, generated)
            results.append(result)
        
        # 가중 평균
        utility = sum(r.utility * w for r, w in zip(results, self.weights))
        style = sum(r.style * w for r, w in zip(results, self.weights))
        overall = sum(r.overall * w for r, w in zip(results, self.weights))
        
        # 세부 정보 통합
        details = {
            "evaluators": [r.metadata["evaluator"] for r in results],
            "individual_scores": [
                {"utility": r.utility, "style": r.style} 
                for r in results
            ],
            "weights": self.weights
        }
        
        return EvaluationResult(
            utility=utility,
            style=style,
            overall=overall,
            details=details,
            metadata={
                "evaluator": "HybridEvaluator",
                "version": self.version,
                "num_evaluators": len(self.evaluators)
            }
        )


# ============================================================
# 6. 평가기 레지스트리 (플러그인 등록 시스템)
# ============================================================

class EvaluatorRegistry:
    """
    평가기 레지스트리
    
    새로운 평가기를 등록하고 관리하는 시스템
    """
    
    _registry = {}
    
    @classmethod
    def register(cls, name: str, evaluator_class: type):
        """
        평가기 등록
        
        Args:
            name: 평가기 이름 (예: "keyword", "gpt4")
            evaluator_class: 평가기 클래스
        """
        if not issubclass(evaluator_class, BaseEvaluator):
            raise ValueError(f"{evaluator_class}는 BaseEvaluator를 상속받아야 합니다.")
        
        cls._registry[name] = evaluator_class
        print(f"✅ 평가기 등록: {name} → {evaluator_class.__name__}")
    
    @classmethod
    def get(cls, name: str) -> type:
        """등록된 평가기 가져오기"""
        if name not in cls._registry:
            raise ValueError(f"등록되지 않은 평가기: {name}\n"
                           f"사용 가능: {list(cls._registry.keys())}")
        return cls._registry[name]
    
    @classmethod
    def list_evaluators(cls) -> List[str]:
        """등록된 평가기 목록"""
        return list(cls._registry.keys())


# 기본 평가기 등록
EvaluatorRegistry.register("keyword", KeywordEvaluator)
EvaluatorRegistry.register("llm", LLMEvaluator)
EvaluatorRegistry.register("hybrid", HybridEvaluator)


# ============================================================
# 7. 평가기 팩토리 (생성 패턴)
# ============================================================

class EvaluatorFactory:
    """
    평가기 팩토리
    
    설정에 따라 적절한 평가기를 생성합니다.
    """
    
    @staticmethod
    def create(evaluator_type: str, config: Optional[Dict] = None) -> BaseEvaluator:
        """
        평가기 생성
        
        Args:
            evaluator_type: 평가기 타입 ("keyword", "llm", "hybrid" 등)
            config: 평가기 설정
            
        Returns:
            BaseEvaluator 인스턴스
            
        Examples:
            # 키워드 기반
            evaluator = EvaluatorFactory.create("keyword")
            
            # LLM 기반
            evaluator = EvaluatorFactory.create("llm", {
                "provider": "openai",
                "model": "gpt-4",
                "api_key": "sk-..."
            })
            
            # 하이브리드
            evaluator = EvaluatorFactory.create("hybrid", {
                "evaluators": [
                    {"type": "keyword", "weight": 0.3},
                    {"type": "llm", "weight": 0.7}
                ]
            })
        """
        evaluator_class = EvaluatorRegistry.get(evaluator_type)
        return evaluator_class(config)
    
    @staticmethod
    def create_from_config_file(config_path: str) -> BaseEvaluator:
        """
        설정 파일에서 평가기 생성
        
        Args:
            config_path: JSON 설정 파일 경로
            
        Returns:
            BaseEvaluator 인스턴스
        """
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        evaluator_type = config.get("type", "keyword")
        return EvaluatorFactory.create(evaluator_type, config)


# ============================================================
# 8. 사용 예시
# ============================================================

def example_usage():
    """플러그인 기반 평가 시스템 사용 예시"""
    
    print("="*60)
    print("플러그인 기반 평가 시스템 - 사용 예시")
    print("="*60)
    
    # 테스트 데이터
    original = "Novel deep learning approach achieving state-of-the-art NLP results."
    generated = "New deep learning method for NLP tasks with improved performance."
    
    # ========================================
    # 1. 키워드 기반 평가 (현재 방식)
    # ========================================
    
    print("\n1. 키워드 기반 평가")
    print("-" * 60)
    
    evaluator_keyword = EvaluatorFactory.create("keyword")
    result = evaluator_keyword.evaluate(original, generated)
    
    print(f"평가기: {result.metadata['evaluator']}")
    print(f"유용성: {result.utility:.1f}%")
    print(f"스타일: {result.style:.1f}%")
    print(f"전체: {result.overall:.1f}%")
    
    # ========================================
    # 2. LLM 기반 평가 (향후)
    # ========================================
    
    print("\n2. LLM 기반 평가 (향후 구현)")
    print("-" * 60)
    
    # 아직 구현 안됨 → fallback
    evaluator_llm = EvaluatorFactory.create("llm", {
        "provider": "openai",
        "model": "gpt-4"
    })
    result = evaluator_llm.evaluate(original, generated)
    
    print(f"평가기: {result.metadata['evaluator']}")
    print(f"유용성: {result.utility:.1f}%")
    
    # ========================================
    # 3. 하이브리드 평가 (조합)
    # ========================================
    
    print("\n3. 하이브리드 평가 (여러 방식 조합)")
    print("-" * 60)
    
    evaluator_hybrid = EvaluatorFactory.create("hybrid", {
        "evaluators": [
            {"type": "keyword", "weight": 0.7},
            {"type": "llm", "weight": 0.3}
        ]
    })
    result = evaluator_hybrid.evaluate(original, generated)
    
    print(f"평가기: {result.metadata['evaluator']}")
    print(f"유용성: {result.utility:.1f}%")
    print(f"스타일: {result.style:.1f}%")
    print(f"사용된 평가기: {result.details['evaluators']}")
    
    # ========================================
    # 4. 등록된 평가기 목록
    # ========================================
    
    print("\n4. 등록된 평가기 목록")
    print("-" * 60)
    
    evaluators = EvaluatorRegistry.list_evaluators()
    print(f"사용 가능한 평가기: {evaluators}")
    
    # ========================================
    # 5. 하위 호환성 (기존 코드)
    # ========================================
    
    print("\n5. 하위 호환성 (기존 코드와 동일한 형식)")
    print("-" * 60)
    
    evaluator = EvaluatorFactory.create("keyword")
    result = evaluator.evaluate(original, generated)
    
    # 기존 코드와 동일한 딕셔너리 형식
    result_dict = result.to_dict()
    print(f"유용성: {result_dict['utility']:.1f}%")
    print(f"스타일: {result_dict['style']:.1f}%")
    print(f"단어 수: {result_dict['word_count']}")
    
    print("\n" + "="*60)
    print("✅ 사용 예시 완료!")
    print("="*60)


# ============================================================
# 9. 새로운 평가기 추가하는 방법 (예시)
# ============================================================

class CustomEvaluator(BaseEvaluator):
    """
    커스텀 평가기 예시
    
    팀원이 새로운 평가 방식을 추가하는 방법을 보여줍니다.
    """
    
    def evaluate(self, original: str, generated: str) -> EvaluationResult:
        """커스텀 평가 로직"""
        # 여기에 새로운 평가 방식 구현
        utility = 80.0  # 예시
        style = 75.0  # 예시
        overall = (utility + style) / 2
        
        return EvaluationResult(
            utility=utility,
            style=style,
            overall=overall,
            details={"method": "custom"},
            metadata={"evaluator": "CustomEvaluator", "version": "1.0.0"}
        )


# 새로운 평가기 등록 (사용 전에 등록!)
# EvaluatorRegistry.register("custom", CustomEvaluator)


if __name__ == "__main__":
    # 사용 예시 실행
    example_usage()