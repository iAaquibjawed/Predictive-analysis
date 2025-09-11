import logging
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
import httpx

logger = logging.getLogger(__name__)

class LiteratureService:
    """
    Service for accessing medical literature and research papers
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"  # PubMed API
        self.api_key = None  # In production, this would be loaded from environment
        self.cache = {}  # Simple cache for demo purposes

        # Initialize literature database
        self._init_literature_database()

    def _init_literature_database(self):
        """Initialize the medical literature database"""

        self.literature_database = {
            "diabetes": [
                {
                    "pmid": "12345678",
                    "title": "Metformin for Type 2 Diabetes: A Systematic Review and Meta-analysis",
                    "authors": ["Smith J", "Johnson A", "Brown K", "Davis M"],
                    "journal": "Diabetes Care",
                    "year": 2023,
                    "volume": "46",
                    "issue": "3",
                    "pages": "456-468",
                    "abstract": "This systematic review and meta-analysis evaluated the efficacy and safety of metformin in the management of type 2 diabetes. The study included 25 randomized controlled trials with over 10,000 participants. Results showed that metformin significantly reduced HbA1c levels compared to placebo and was associated with weight loss and improved cardiovascular outcomes.",
                    "keywords": ["metformin", "type 2 diabetes", "systematic review", "meta-analysis"],
                    "evidence_level": "A",
                    "doi": "10.1000/diabetes.2023.001",
                    "url": "https://doi.org/10.1000/diabetes.2023.001",
                    "study_type": "Systematic Review",
                    "sample_size": 10000,
                    "primary_outcomes": ["HbA1c reduction", "Weight loss", "Cardiovascular events"],
                    "conclusions": "Metformin is an effective first-line therapy for type 2 diabetes with favorable safety profile and cardiovascular benefits."
                },
                {
                    "pmid": "12345679",
                    "title": "Lifestyle Interventions in Diabetes Prevention: A Randomized Controlled Trial",
                    "authors": ["Davis M", "Wilson P", "Taylor R", "Anderson L"],
                    "journal": "New England Journal of Medicine",
                    "year": 2022,
                    "volume": "387",
                    "issue": "15",
                    "pages": "1392-1403",
                    "abstract": "This randomized controlled trial evaluated the effectiveness of intensive lifestyle intervention in preventing type 2 diabetes in high-risk individuals. The study randomized 1,000 participants to either intensive lifestyle intervention or standard care. After 3 years, the intervention group had a 58% reduction in diabetes incidence.",
                    "keywords": ["diabetes prevention", "lifestyle intervention", "randomized controlled trial"],
                    "evidence_level": "A",
                    "doi": "10.1000/nejm.2022.001",
                    "url": "https://doi.org/10.1000/nejm.2022.001",
                    "study_type": "Randomized Controlled Trial",
                    "sample_size": 1000,
                    "primary_outcomes": ["Diabetes incidence", "Weight loss", "Physical activity"],
                    "conclusions": "Intensive lifestyle intervention significantly reduces the risk of type 2 diabetes in high-risk individuals."
                }
            ],
            "hypertension": [
                {
                    "pmid": "12345680",
                    "title": "ACE Inhibitors in Hypertension Management: A Network Meta-analysis",
                    "authors": ["Anderson L", "Miller S", "Clark J", "White R"],
                    "journal": "Hypertension",
                    "year": 2023,
                    "volume": "81",
                    "issue": "2",
                    "pages": "234-245",
                    "abstract": "This network meta-analysis compared the efficacy of different ACE inhibitors in the management of hypertension. The study included 45 trials with over 25,000 participants. Results showed that all ACE inhibitors were effective in reducing blood pressure, with lisinopril and enalapril showing the most consistent results.",
                    "keywords": ["ACE inhibitors", "hypertension", "network meta-analysis", "blood pressure"],
                    "evidence_level": "A",
                    "doi": "10.1000/hypertension.2023.001",
                    "url": "https://doi.org/10.1000/hypertension.2023.001",
                    "study_type": "Network Meta-analysis",
                    "sample_size": 25000,
                    "primary_outcomes": ["Systolic blood pressure reduction", "Diastolic blood pressure reduction", "Adverse events"],
                    "conclusions": "ACE inhibitors are effective antihypertensive agents with lisinopril and enalapril showing the most consistent efficacy."
                }
            ],
            "hyperlipidemia": [
                {
                    "pmid": "12345681",
                    "title": "Statin Therapy for Cardiovascular Risk Reduction: A Comprehensive Review",
                    "authors": ["Thompson K", "Martin P", "Lee S", "Garcia M"],
                    "journal": "Journal of the American College of Cardiology",
                    "year": 2023,
                    "volume": "82",
                    "issue": "8",
                    "pages": "678-689",
                    "abstract": "This comprehensive review examined the evidence for statin therapy in cardiovascular risk reduction. The review covered primary and secondary prevention studies, showing consistent benefits across different patient populations and risk levels.",
                    "keywords": ["statins", "cardiovascular disease", "risk reduction", "primary prevention"],
                    "evidence_level": "A",
                    "doi": "10.1000/jacc.2023.001",
                    "url": "https://doi.org/10.1000/jacc.2023.001",
                    "study_type": "Comprehensive Review",
                    "sample_size": 50000,
                    "primary_outcomes": ["Cardiovascular events", "All-cause mortality", "LDL-C reduction"],
                    "conclusions": "Statin therapy provides significant cardiovascular benefits in both primary and secondary prevention settings."
                }
            ],
            "asthma": [
                {
                    "pmid": "12345682",
                    "title": "Inhaled Corticosteroids in Asthma: Efficacy and Safety Profile",
                    "authors": ["Roberts N", "Harris T", "Lewis M", "Turner J"],
                    "journal": "Thorax",
                    "year": 2023,
                    "volume": "78",
                    "issue": "5",
                    "pages": "445-456",
                    "abstract": "This study evaluated the efficacy and safety of inhaled corticosteroids in the management of asthma. The research included data from clinical trials and real-world studies, showing consistent benefits in symptom control and lung function improvement.",
                    "keywords": ["asthma", "inhaled corticosteroids", "efficacy", "safety"],
                    "evidence_level": "A",
                    "doi": "10.1000/thorax.2023.001",
                    "url": "https://doi.org/10.1000/thorax.2023.001",
                    "study_type": "Systematic Review",
                    "sample_size": 15000,
                    "primary_outcomes": ["Asthma control", "Lung function", "Exacerbation rate"],
                    "conclusions": "Inhaled corticosteroids are effective and safe for long-term asthma management."
                }
            ]
        }

    async def search_literature(
        self,
        query: str,
        condition: Optional[str] = None,
        year_from: Optional[int] = None,
        year_to: Optional[int] = None,
        evidence_level: Optional[str] = None,
        study_type: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Search medical literature based on various criteria
        """
        try:
            results = []
            query_lower = query.lower()

            # Search in literature database
            for condition_key, publications in self.literature_database.items():
                # Filter by condition if specified
                if condition and condition.lower() != condition_key.lower():
                    continue

                for publication in publications:
                    # Apply filters
                    if year_from and publication["year"] < year_from:
                        continue

                    if year_to and publication["year"] > year_to:
                        continue

                    if evidence_level and publication["evidence_level"] != evidence_level:
                        continue

                    if study_type and publication["study_type"] != study_type:
                        continue

                    # Search in title, abstract, and keywords
                    searchable_text = (
                        publication.get("title", "") +
                        " " + publication.get("abstract", "") +
                        " " + " ".join(publication.get("keywords", []))
                    ).lower()

                    if query_lower in searchable_text:
                        results.append(publication)

                        if len(results) >= limit:
                            break

                if len(results) >= limit:
                    break

            # Sort by year (newest first) and evidence level
            results.sort(key=lambda x: (x["year"], x["evidence_level"]), reverse=True)

            return results[:limit]

        except Exception as e:
            self.logger.error(f"Literature search failed: {e}")
            raise

    async def get_publication_by_pmid(self, pmid: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific publication by PMID
        """
        try:
            for condition, publications in self.literature_database.items():
                for publication in publications:
                    if publication["pmid"] == pmid:
                        return publication

            return None

        except Exception as e:
            self.logger.error(f"Failed to get publication by PMID {pmid}: {e}")
            raise

    async def get_publications_by_author(
        self,
        author_name: str,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Get publications by a specific author
        """
        try:
            results = []
            author_lower = author_name.lower()

            for condition, publications in self.literature_database.items():
                for publication in publications:
                    authors = publication.get("authors", [])
                    if any(author_lower in author.lower() for author in authors):
                        results.append(publication)

                        if len(results) >= limit:
                            break

                if len(results) >= limit:
                    break

            # Sort by year (newest first)
            results.sort(key=lambda x: x["year"], reverse=True)

            return results[:limit]

        except Exception as e:
            self.logger.error(f"Failed to get publications by author {author_name}: {e}")
            raise

    async def get_publications_by_journal(
        self,
        journal_name: str,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Get publications from a specific journal
        """
        try:
            results = []
            journal_lower = journal_name.lower()

            for condition, publications in self.literature_database.items():
                for publication in publications:
                    if journal_lower in publication.get("journal", "").lower():
                        results.append(publication)

                        if len(results) >= limit:
                            break

                if len(results) >= limit:
                    break

            # Sort by year (newest first)
            results.sort(key=lambda x: x["year"], reverse=True)

            return results[:limit]

        except Exception as e:
            self.logger.error(f"Failed to get publications by journal {journal_name}: {e}")
            raise

    async def get_recent_publications(
        self,
        days: int = 30,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Get recently published literature
        """
        try:
            # Mock recent publications - in production, this would use real dates
            current_date = datetime.now()
            cutoff_date = current_date.replace(year=current_date.year - 1)  # Mock: last year

            results = []

            for condition, publications in self.literature_database.items():
                for publication in publications:
                    # Mock publication date
                    pub_date = datetime(publication["year"], 1, 1)

                    if pub_date >= cutoff_date:
                        results.append(publication)

                        if len(results) >= limit:
                            break

                if len(results) >= limit:
                    break

            # Sort by year (newest first)
            results.sort(key=lambda x: x["year"], reverse=True)

            return results[:limit]

        except Exception as e:
            self.logger.error(f"Failed to get recent publications: {e}")
            raise

    async def get_evidence_summary(
        self,
        condition: str,
        topic: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get evidence summary for a condition or topic
        """
        try:
            summary = {
                "condition": condition,
                "topic": topic,
                "total_publications": 0,
                "evidence_levels": {},
                "study_types": {},
                "key_findings": [],
                "recommendations": [],
                "gaps_in_evidence": []
            }

            # Get relevant publications
            publications = await self.search_literature(
                query=condition,
                condition=condition,
                limit=100
            )

            if topic:
                topic_publications = await self.search_literature(
                    query=topic,
                    condition=condition,
                    limit=100
                )
                # Merge and deduplicate
                all_pubs = {pub["pmid"]: pub for pub in publications + topic_publications}.values()
            else:
                all_pubs = publications

            summary["total_publications"] = len(all_pubs)

            # Analyze evidence levels
            for pub in all_pubs:
                evidence_level = pub.get("evidence_level", "Unknown")
                summary["evidence_levels"][evidence_level] = summary["evidence_levels"].get(evidence_level, 0) + 1

            # Analyze study types
            for pub in all_pubs:
                study_type = pub.get("study_type", "Unknown")
                summary["study_types"][study_type] = summary["study_types"].get(study_type, 0) + 1

            # Extract key findings
            for pub in all_pubs:
                if pub.get("conclusions"):
                    summary["key_findings"].append({
                        "pmid": pub["pmid"],
                        "title": pub["title"],
                        "conclusion": pub["conclusions"],
                        "evidence_level": pub.get("evidence_level", "Unknown")
                    })

            # Generate recommendations
            high_evidence_pubs = [pub for pub in all_pubs if pub.get("evidence_level") == "A"]
            if high_evidence_pubs:
                summary["recommendations"].append("Strong evidence supports current treatment approaches")
            else:
                summary["recommendations"].append("Consider lower evidence levels when making clinical decisions")

            # Identify gaps
            if len(all_pubs) < 10:
                summary["gaps_in_evidence"].append("Limited evidence available for this condition/topic")

            if not any(pub.get("evidence_level") == "A" for pub in all_pubs):
                summary["gaps_in_evidence"].append("Lack of high-level evidence (Level A)")

            return summary

        except Exception as e:
            self.logger.error(f"Failed to get evidence summary: {e}")
            raise

    async def get_systematic_reviews(
        self,
        condition: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Get systematic reviews and meta-analyses
        """
        try:
            results = []

            for condition_key, publications in self.literature_database.items():
                # Filter by condition if specified
                if condition and condition.lower() != condition_key.lower():
                    continue

                for publication in publications:
                    study_type = publication.get("study_type", "").lower()
                    if "systematic review" in study_type or "meta-analysis" in study_type:
                        results.append(publication)

                        if len(results) >= limit:
                            break

                if len(results) >= limit:
                    break

            # Sort by year (newest first)
            results.sort(key=lambda x: x["year"], reverse=True)

            return results[:limit]

        except Exception as e:
            self.logger.error(f"Failed to get systematic reviews: {e}")
            raise

    async def get_randomized_trials(
        self,
        condition: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Get randomized controlled trials
        """
        try:
            results = []

            for condition_key, publications in self.literature_database.items():
                # Filter by condition if specified
                if condition and condition.lower() != condition_key.lower():
                    continue

                for publication in publications:
                    study_type = publication.get("study_type", "").lower()
                    if "randomized controlled trial" in study_type or "rct" in study_type:
                        results.append(publication)

                        if len(results) >= limit:
                            break

                if len(results) >= limit:
                    break

            # Sort by year (newest first)
            results.sort(key=lambda x: x["year"], reverse=True)

            return results[:limit]

        except Exception as e:
            self.logger.error(f"Failed to get randomized trials: {e}")
            raise

    async def get_clinical_guidelines_references(
        self,
        condition: str
    ) -> List[Dict[str, Any]]:
        """
        Get literature references that support clinical guidelines
        """
        try:
            # Mock clinical guidelines references
            guidelines_references = {
                "diabetes": [
                    {
                        "guideline": "NICE NG28 - Type 2 diabetes in adults: management",
                        "references": [
                            {"pmid": "12345678", "title": "Metformin for Type 2 Diabetes: A Systematic Review"},
                            {"pmid": "12345679", "title": "Lifestyle Interventions in Diabetes Prevention"}
                        ]
                    }
                ],
                "hypertension": [
                    {
                        "guideline": "NICE NG136 - Hypertension in adults: diagnosis and management",
                        "references": [
                            {"pmid": "12345680", "title": "ACE Inhibitors in Hypertension Management"}
                        ]
                    }
                ]
            }

            return guidelines_references.get(condition.lower(), [])

        except Exception as e:
            self.logger.error(f"Failed to get clinical guidelines references: {e}")
            raise

    async def get_research_trends(
        self,
        condition: str,
        years: int = 5
    ) -> Dict[str, Any]:
        """
        Get research trends for a condition over time
        """
        try:
            trends = {
                "condition": condition,
                "years": years,
                "publication_counts": {},
                "study_type_trends": {},
                "evidence_level_trends": {},
                "key_topics": []
            }

            # Get publications for the condition
            publications = await self.search_literature(
                query=condition,
                condition=condition,
                limit=1000
            )

            # Calculate publication counts by year
            current_year = datetime.now().year
            for year in range(current_year - years + 1, current_year + 1):
                year_pubs = [pub for pub in publications if pub["year"] == year]
                trends["publication_counts"][year] = len(year_pubs)

            # Calculate study type trends
            for pub in publications:
                study_type = pub.get("study_type", "Unknown")
                year = pub["year"]
                if year not in trends["study_type_trends"]:
                    trends["study_type_trends"][year] = {}
                trends["study_type_trends"][year][study_type] = trends["study_type_trends"][year].get(study_type, 0) + 1

            # Calculate evidence level trends
            for pub in publications:
                evidence_level = pub.get("evidence_level", "Unknown")
                year = pub["year"]
                if year not in trends["evidence_level_trends"]:
                    trends["evidence_level_trends"][year] = {}
                trends["evidence_level_trends"][year][evidence_level] = trends["evidence_level_trends"][year].get(evidence_level, 0) + 1

            # Identify key topics
            all_keywords = []
            for pub in publications:
                all_keywords.extend(pub.get("keywords", []))

            # Count keyword frequency
            keyword_counts = {}
            for keyword in all_keywords:
                keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1

            # Get top keywords
            top_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            trends["key_topics"] = [keyword for keyword, count in top_keywords]

            return trends

        except Exception as e:
            self.logger.error(f"Failed to get research trends: {e}")
            raise

    async def get_literature_metadata(self) -> Dict[str, Any]:
        """
        Get metadata about available literature
        """
        try:
            metadata = {
                "total_publications": sum(
                    len(publications) for publications in self.literature_database.values()
                ),
                "conditions_covered": list(self.literature_database.keys()),
                "year_range": {
                    "min": min(
                        pub["year"] for publications in self.literature_database.values()
                        for pub in publications
                    ),
                    "max": max(
                        pub["year"] for publications in self.literature_database.values()
                        for pub in publications
                    )
                },
                "journals": list(set(
                    pub.get("journal", "Unknown")
                    for publications in self.literature_database.values()
                    for pub in publications
                )),
                "evidence_levels": list(set(
                    pub.get("evidence_level", "Unknown")
                    for publications in self.literature_database.values()
                    for pub in publications
                )),
                "study_types": list(set(
                    pub.get("study_type", "Unknown")
                    for publications in self.literature_database.values()
                    for pub in publications
                )),
                "last_updated": datetime.now().isoformat()
            }

            return metadata

        except Exception as e:
            self.logger.error(f"Failed to get literature metadata: {e}")
            raise







