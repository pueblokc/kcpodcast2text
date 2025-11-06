"""
NLP service for topic extraction, categorization, and summarization
"""
import re
from typing import List, Dict, Any, Optional, Tuple
from collections import Counter

import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation


# Download required NLTK data (run once)
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)

try:
    nltk.data.find('taggers/averaged_perceptron_tagger')
except LookupError:
    nltk.download('averaged_perceptron_tagger', quiet=True)

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.tag import pos_tag


class NLPService:
    """Service for NLP operations on transcripts"""

    def __init__(self):
        self.stop_words = set(stopwords.words('english'))
        self.categories = {
            'technology': ['tech', 'software', 'computer', 'programming', 'ai', 'data', 'code', 'digital', 'app', 'internet'],
            'health': ['health', 'fitness', 'medical', 'doctor', 'exercise', 'nutrition', 'wellness', 'disease', 'mental'],
            'business': ['business', 'startup', 'entrepreneur', 'company', 'market', 'finance', 'investment', 'economy'],
            'science': ['science', 'research', 'study', 'experiment', 'physics', 'chemistry', 'biology', 'discovery'],
            'philosophy': ['philosophy', 'ethics', 'moral', 'existence', 'consciousness', 'meaning', 'truth', 'wisdom'],
            'comedy': ['comedy', 'funny', 'joke', 'humor', 'laugh', 'comedian', 'entertainment'],
            'politics': ['politics', 'government', 'election', 'policy', 'law', 'democracy', 'president', 'congress'],
            'sports': ['sports', 'game', 'team', 'player', 'championship', 'football', 'basketball', 'athlete'],
            'education': ['education', 'learning', 'school', 'university', 'teaching', 'student', 'knowledge', 'course'],
            'arts': ['art', 'music', 'film', 'creative', 'design', 'artist', 'culture', 'movie', 'painting'],
        }

    def extract_keywords(self, text: str, top_n: int = 20) -> List[Tuple[str, float]]:
        """Extract top keywords using TF-IDF"""
        # Preprocess text
        words = word_tokenize(text.lower())
        words = [w for w in words if w.isalnum() and w not in self.stop_words and len(w) > 3]

        if not words:
            return []

        # Create document for TF-IDF
        doc = ' '.join(words)

        try:
            vectorizer = TfidfVectorizer(max_features=top_n, ngram_range=(1, 2))
            tfidf_matrix = vectorizer.fit_transform([doc])
            feature_names = vectorizer.get_feature_names_out()
            scores = tfidf_matrix.toarray()[0]

            # Sort by score
            keyword_scores = list(zip(feature_names, scores))
            keyword_scores.sort(key=lambda x: x[1], reverse=True)

            return keyword_scores[:top_n]
        except:
            # Fallback to simple word frequency
            word_freq = Counter(words)
            return [(word, count / len(words)) for word, count in word_freq.most_common(top_n)]

    def extract_topics(self, text: str, num_topics: int = 3) -> List[Dict[str, Any]]:
        """Extract main topics using LDA"""
        sentences = sent_tokenize(text)

        if len(sentences) < 2:
            return []

        try:
            # Vectorize
            vectorizer = TfidfVectorizer(
                max_features=100,
                stop_words='english',
                ngram_range=(1, 2)
            )
            doc_term_matrix = vectorizer.fit_transform(sentences)

            # LDA
            lda = LatentDirichletAllocation(
                n_components=min(num_topics, len(sentences)),
                random_state=42
            )
            lda.fit(doc_term_matrix)

            # Extract topics
            feature_names = vectorizer.get_feature_names_out()
            topics = []

            for topic_idx, topic in enumerate(lda.components_):
                top_indices = topic.argsort()[-5:][::-1]
                top_words = [feature_names[i] for i in top_indices]
                top_scores = [topic[i] for i in top_indices]

                topics.append({
                    'id': topic_idx,
                    'words': top_words,
                    'scores': top_scores.tolist(),
                    'confidence': float(max(top_scores)),
                })

            return topics
        except:
            return []

    def categorize(self, text: str) -> List[Tuple[str, float]]:
        """Categorize text into predefined categories"""
        text_lower = text.lower()
        words = word_tokenize(text_lower)
        word_set = set(w for w in words if w.isalnum())

        category_scores = []

        for category, keywords in self.categories.items():
            # Count matches
            matches = sum(1 for keyword in keywords if keyword in text_lower)
            score = matches / len(keywords) if keywords else 0
            category_scores.append((category, score))

        # Sort by score
        category_scores.sort(key=lambda x: x[1], reverse=True)

        # Return categories with score > 0
        return [(cat, score) for cat, score in category_scores if score > 0]

    def generate_summary(self, text: str, num_sentences: int = 5) -> str:
        """Generate extractive summary using sentence scoring"""
        sentences = sent_tokenize(text)

        if len(sentences) <= num_sentences:
            return text

        # Score sentences based on keyword frequency
        keywords = [kw for kw, _ in self.extract_keywords(text, top_n=30)]

        sentence_scores = []
        for sentence in sentences:
            words = word_tokenize(sentence.lower())
            score = sum(1 for word in words if word in keywords)
            sentence_scores.append((sentence, score))

        # Sort by score and take top N
        sentence_scores.sort(key=lambda x: x[1], reverse=True)
        top_sentences = sentence_scores[:num_sentences]

        # Maintain original order
        summary_sentences = []
        for sentence in sentences:
            if any(sentence == s for s, _ in top_sentences):
                summary_sentences.append(sentence)
            if len(summary_sentences) >= num_sentences:
                break

        return ' '.join(summary_sentences)

    def extract_named_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract named entities (people, organizations, locations)"""
        sentences = sent_tokenize(text)
        entities = {
            'people': [],
            'organizations': [],
            'locations': [],
        }

        # Simple NER using POS tagging and capitalization
        for sentence in sentences[:50]:  # Limit for performance
            words = word_tokenize(sentence)
            tagged = pos_tag(words)

            current_entity = []
            for word, tag in tagged:
                # Proper nouns
                if tag in ['NNP', 'NNPS']:
                    current_entity.append(word)
                else:
                    if current_entity:
                        entity = ' '.join(current_entity)
                        # Simple heuristic classification
                        if any(title in entity for title in ['Mr.', 'Ms.', 'Dr.', 'Prof.']):
                            entities['people'].append(entity)
                        elif any(org_word in entity for org_word in ['Inc', 'Corp', 'LLC', 'University', 'Institute']):
                            entities['organizations'].append(entity)
                        elif len(current_entity) == 1 and len(entity) > 2:
                            # Single proper noun - could be person or place
                            entities['people'].append(entity)

                        current_entity = []

        # Deduplicate and clean
        for key in entities:
            entities[key] = list(set(entities[key]))
            entities[key] = [e for e in entities[key] if len(e) > 2][:20]  # Top 20

        return entities

    def detect_speakers(self, text: str) -> List[str]:
        """Detect potential speaker names from transcript"""
        # Look for common patterns like "Speaker:", "John:", etc.
        pattern = r'\b([A-Z][a-z]+(?:\s[A-Z][a-z]+)?)\s*:'
        matches = re.findall(pattern, text)

        # Count occurrences
        speaker_counts = Counter(matches)

        # Return speakers mentioned more than once
        speakers = [name for name, count in speaker_counts.items() if count > 1]

        return speakers[:10]  # Top 10 speakers

    def extract_highlights(
        self,
        text: str,
        segments: List[Dict[str, Any]],
        num_highlights: int = 5
    ) -> List[Dict[str, Any]]:
        """Extract highlight segments based on keyword density and importance"""
        if not segments:
            return []

        keywords = set(kw for kw, _ in self.extract_keywords(text, top_n=50))

        highlights = []
        for segment in segments:
            segment_text = segment.get('text', '')
            words = word_tokenize(segment_text.lower())

            # Calculate score
            keyword_matches = sum(1 for word in words if word in keywords)
            score = keyword_matches / len(words) if words else 0

            highlights.append({
                'start': segment.get('start'),
                'end': segment.get('end'),
                'text': segment_text,
                'score': score,
                'reason': f'{keyword_matches} important keywords',
            })

        # Sort by score
        highlights.sort(key=lambda x: x['score'], reverse=True)

        return highlights[:num_highlights]

    def analyze_transcript(
        self,
        text: str,
        segments: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Comprehensive analysis of transcript

        Returns dict with:
        - keywords
        - topics
        - categories
        - short_summary
        - full_summary
        - named_entities
        - speakers
        - highlights
        """
        return {
            'keywords': [kw for kw, _ in self.extract_keywords(text, top_n=30)],
            'topics': self.extract_topics(text, num_topics=5),
            'categories': self.categorize(text),
            'short_summary': self.generate_summary(text, num_sentences=3),
            'full_summary': self.generate_summary(text, num_sentences=7),
            'named_entities': self.extract_named_entities(text),
            'speakers': self.detect_speakers(text),
            'highlights': self.extract_highlights(text, segments or [], num_highlights=5),
        }


# Global NLP service instance
nlp_service = NLPService()
