from sentence_transformers import SentenceTransformer, util

class SmartEvaluator:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        # Load the pre-trained Sentence Transformer model
        # Using a lightweight model for better performance in a local environment
        self.model = SentenceTransformer(model_name)

    def evaluate_descriptive(self, student_answer, model_answer):
        """
        Calculates semantic similarity between the student's answer and the model's answer.
        Returns a suggested score (0.0 to 1.0).
        """
        if not student_answer or not model_answer:
            return 0.0
            
        # Compute embeddings
        embeddings1 = self.model.encode(student_answer, convert_to_tensor=True)
        embeddings2 = self.model.encode(model_answer, convert_to_tensor=True)
        
        # Calculate cosine similarity
        cosine_score = util.cos_sim(embeddings1, embeddings2)
        
        # Scale to 0-1 and return
        score = float(cosine_score[0][0])
        return max(0.0, min(1.0, score))

# Example usage (standalone test)
if __name__ == "__main__":
    evaluator = SmartEvaluator()
    q1 = "The brain of the computer is the central processing unit."
    a1 = "CPU is the main processing unit and brain of a computer system."
    a2 = "The RAM stores data temporarily for the CPU."
    
    print(f"Similarity (Correct): {evaluator.evaluate_descriptive(a1, q1):.2f}")
    print(f"Similarity (Incorrect): {evaluator.evaluate_descriptive(a2, q1):.2f}")
