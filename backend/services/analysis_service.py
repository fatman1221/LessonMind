from sklearn.tree import DecisionTreeClassifier
import pandas as pd
import numpy as np
from typing import Dict, List
import json


class LearningAnalysisService:
    """学情分析服务"""
    
    def __init__(self):
        self.model = DecisionTreeClassifier(max_depth=5, random_state=42)
        self.is_trained = False

    @staticmethod
    def _clamp01(value: float) -> float:
        """将分值限制在 0~1 区间。"""
        return float(max(0.0, min(1.0, value)))
    
    def prepare_features(self, student_data: Dict) -> np.ndarray:
        """准备特征数据"""
        features = []
        
        # 作业成绩特征
        homework_scores = student_data.get("homework_scores", {})
        if homework_scores:
            scores = list(homework_scores.values())
            features.extend([
                np.mean(scores) if scores else 0,  # 平均分
                np.std(scores) if len(scores) > 1 else 0,  # 标准差
                len(scores),  # 作业次数
            ])
        else:
            features.extend([0, 0, 0])
        
        # 学习行为特征
        behavior = student_data.get("learning_behavior", {})
        features.extend([
            behavior.get("study_time", 0),  # 学习时长
            behavior.get("question_count", 0),  # 提问次数
            behavior.get("participation_rate", 0),  # 参与度
        ])
        
        return np.array(features).reshape(1, -1)
    
    def train_model(self, training_data: List[Dict]):
        """训练模型"""
        if not training_data:
            return
        
        X = []
        y = []
        
        for data in training_data:
            features = self.prepare_features(data)
            X.append(features[0])
            
            # 根据知识点掌握情况计算标签
            mastery = data.get("knowledge_mastery", {})
            if mastery:
                avg_mastery = np.mean(list(mastery.values()))
                # 0: 未掌握, 1: 部分掌握, 2: 掌握
                if avg_mastery >= 0.85:
                    y.append(2)
                elif avg_mastery >= 0.6:
                    y.append(1)
                else:
                    y.append(0)
            else:
                y.append(0)
        
        if X and y:
            X = np.array(X)
            y = np.array(y)
            self.model.fit(X, y)
            self.is_trained = True
    
    def analyze_student(self, student_data: Dict) -> Dict:
        """分析学生学情"""
        # 如果没有训练数据，使用规则方法
        if not self.is_trained:
            return self._rule_based_analysis(student_data)
        
        features = self.prepare_features(student_data)
        prediction = self.model.predict(features)[0]
        
        # 获取预测概率
        probabilities = self.model.predict_proba(features)[0]
        
        # 分析结果
        mastery_levels = ["未掌握", "部分掌握", "掌握"]
        mastery_level = mastery_levels[prediction]
        
        # 计算知识掌握度
        knowledge_mastery = student_data.get("knowledge_mastery", {})
        if knowledge_mastery:
            avg_mastery = np.mean(list(knowledge_mastery.values()))
        else:
            avg_mastery = probabilities[prediction]
        
        # 学习能力评估
        homework_scores = student_data.get("homework_scores", {})
        behavior = student_data.get("learning_behavior", {})
        
        ability_score = 0
        if homework_scores:
            scores = list(homework_scores.values())
            # 作业分数通常是 0~100，先归一化到 0~1
            ability_score += (np.mean(scores) / 100.0) * 0.5
        
        if behavior:
            ability_score += behavior.get("participation_rate", 0) * 0.3
            ability_score += min(behavior.get("study_time", 0) / 10, 1) * 0.2
        ability_score = self._clamp01(ability_score)
        
        # 学习习惯评估
        habit_score = 0
        if behavior:
            habit_score += min(behavior.get("study_time", 0) / 20, 1) * 0.4
            habit_score += min(behavior.get("question_count", 0) / 10, 1) * 0.3
            habit_score += behavior.get("participation_rate", 0) * 0.3
        habit_score = self._clamp01(habit_score)
        
        return {
            "mastery_level": mastery_level,
            "mastery_score": self._clamp01(float(avg_mastery)),
            "ability_score": float(ability_score),
            "habit_score": float(habit_score),
            "prediction_confidence": float(probabilities[prediction]),
            "recommendations": self._generate_recommendations(mastery_level, avg_mastery, ability_score)
        }
    
    def _rule_based_analysis(self, student_data: Dict) -> Dict:
        """基于规则的分析（当模型未训练时）"""
        homework_scores = student_data.get("homework_scores", {})
        behavior = student_data.get("learning_behavior", {})
        knowledge_mastery = student_data.get("knowledge_mastery", {})
        
        # 计算知识掌握度
        if knowledge_mastery:
            avg_mastery = np.mean(list(knowledge_mastery.values()))
        elif homework_scores:
            scores = list(homework_scores.values())
            avg_mastery = np.mean(scores) / 100
        else:
            avg_mastery = 0.5
        
        # 确定掌握水平
        if avg_mastery >= 0.85:
            mastery_level = "掌握"
        elif avg_mastery >= 0.6:
            mastery_level = "部分掌握"
        else:
            mastery_level = "未掌握"
        
        # 学习能力评估
        ability_score = 0
        if homework_scores:
            scores = list(homework_scores.values())
            # 作业分数通常是 0~100，先归一化到 0~1
            ability_score += (np.mean(scores) / 100.0) * 0.5
        
        if behavior:
            ability_score += behavior.get("participation_rate", 0) * 0.3
            ability_score += min(behavior.get("study_time", 0) / 10, 1) * 0.2
        ability_score = self._clamp01(ability_score)
        
        # 学习习惯评估
        habit_score = 0
        if behavior:
            habit_score += min(behavior.get("study_time", 0) / 20, 1) * 0.4
            habit_score += min(behavior.get("question_count", 0) / 10, 1) * 0.3
            habit_score += behavior.get("participation_rate", 0) * 0.3
        habit_score = self._clamp01(habit_score)
        
        return {
            "mastery_level": mastery_level,
            "mastery_score": self._clamp01(float(avg_mastery)),
            "ability_score": float(ability_score),
            "habit_score": float(habit_score),
            "prediction_confidence": 0.8,
            "recommendations": self._generate_recommendations(mastery_level, avg_mastery, ability_score)
        }
    
    def _generate_recommendations(
        self,
        mastery_level: str,
        mastery_score: float,
        ability_score: float
    ) -> List[str]:
        """生成学习建议"""
        recommendations = []
        
        if mastery_score < 0.6:
            recommendations.append("建议加强基础知识学习，多进行基础练习")
            recommendations.append("推荐观看相关教学视频，巩固基础概念")
        elif mastery_score < 0.85:
            recommendations.append("建议进行综合练习，提高知识应用能力")
            recommendations.append("可以尝试挑战性题目，拓展思维")
        else:
            recommendations.append("基础扎实，可以进行拓展学习")
            recommendations.append("建议帮助其他同学，教学相长")
        
        if ability_score < 0.5:
            recommendations.append("建议提高学习参与度，多与老师同学交流")
        
        return recommendations


analysis_service = LearningAnalysisService()

