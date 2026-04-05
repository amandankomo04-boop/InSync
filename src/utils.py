import numpy as np

def calculate_cosine_similarity(vec_a, vec_b):
    """
    Implements the Cosine Similarity formula: 
    Dot Product (A, B) / (Norm(A) * Norm(B))
    """
    # Ensure vectors are flattened numpy arrays
    a = np.array(vec_a).flatten()
    b = np.array(vec_b).flatten()
    
    # Calculate Dot Product
    dot_product = np.dot(a, b)
    
    # Calculate Magnitudes (Euclidean Norms)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    
    # Avoid division by zero errors
    if norm_a == 0 or norm_b == 0:
        return 0.0
        
    return dot_product / (norm_a * norm_b)