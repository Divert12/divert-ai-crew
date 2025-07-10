"""
Équipe CrewAI pour générer un pitch marketing complet pour Divert.ai
Version améliorée avec support du paramètre topic
"""

from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool
from langchain_huggingface import HuggingFaceEndpoint
import os
from typing import Dict, Any, Optional


# Configuration du modèle
MODEL = "mistralai/Mixtral-8x7B-Instruct-v0.1"
HF_TOKEN = os.getenv("HF_TOKEN")

# Configuration du LLM
llm = HuggingFaceEndpoint(
    repo_id=MODEL,
    temperature=0.7,
    max_new_tokens=1024,
    huggingfacehub_api_token=HF_TOKEN
)

# Outil de recherche
search_tool = SerperDevTool()

def create_problem_finder_agent():
    """Agent pour identifier les problèmes actuels des entreprises"""
    return Agent(
        role="Problem Finder - Analyste des défis entreprise",
        goal="Identifier 3-5 problèmes concrets que rencontrent les entreprises et particuliers dans leur domaine spécifique, en se concentrant sur la productivité, gestion, automatisation et complexité des outils digitaux.",
        backstory="""Tu es un consultant expérimenté qui a travaillé avec des centaines d'entreprises de toutes tailles. 
        Tu comprends parfaitement les défis opérationnels auxquels font face les PME, freelances et équipes.
        Ta spécialité est d'identifier les vrais problèmes qui freinent la productivité au quotidien dans des secteurs spécifiques.""",
        verbose=True,
        allow_delegation=False,
        tools=[search_tool],
        llm=llm
    )

def create_solution_presenter_agent():
    """Agent pour présenter la solution Divert.ai"""
    return Agent(
        role="Solution Presenter - Expert produit Divert.ai",
        goal="Expliquer comment Divert.ai résout concrètement les problèmes identifiés grâce à ses équipes d'agents IA préconstruits et son interface accessible, en adaptant le message au domaine spécifique.",
        backstory="""Tu es le directeur produit de Divert.ai et tu maîtrises parfaitement la valeur ajoutée du service.
        Tu sais comment transformer les défis business en opportunités grâce à l'IA accessible.
        Tu excelles à expliquer des concepts techniques de manière simple et convaincante, en adaptant ton discours à différents secteurs.""",
        verbose=True,
        allow_delegation=False,
        llm=llm
    )

def create_marketing_advisor_agent():
    """Agent pour proposer des stratégies marketing"""
    return Agent(
        role="Marketing Advisor - Stratège acquisition",
        goal="Proposer des astuces marketing innovantes et efficaces pour attirer les premiers utilisateurs dans le secteur ciblé et les fidéliser.",
        backstory="""Tu es un growth hacker expérimenté qui a lancé plusieurs startups B2B avec succès.
        Tu connais parfaitement les stratégies pour acquérir rapidement des PME, freelances et équipes dans différents secteurs.
        Tu privilégies les approches simples, à faible coût et à fort impact, adaptées au marché cible.""",
        verbose=True,
        allow_delegation=False,
        tools=[search_tool],
        llm=llm
    )

def create_pitch_synthesizer_agent():
    """Agent pour synthétiser le pitch final"""
    return Agent(
        role="Pitch Synthesizer - Rédacteur commercial",
        goal="Compiler tous les éléments en un pitch final fluide, clair et impactant prêt à être présenté, adapté au secteur et public cible.",
        backstory="""Tu es un rédacteur commercial expert qui a créé des centaines de pitches gagnants.
        Tu maîtrises l'art de structurer un discours commercial qui capte l'attention et convainc.
        Tu sais comment équilibrer professionnalisme, optimisme et accessibilité tout en personnalisant le message.""",
        verbose=True,
        allow_delegation=False,
        llm=llm
    )

def create_problem_identification_task(agent, topic: str):
    """Tâche d'identification des problèmes adaptée au topic"""
    return Task(
        description=f"""Identifie 3 à 5 problèmes concrets et actuels que rencontrent les entreprises (PME, freelances, équipes) 
        dans le secteur/domaine suivant : {topic}
        
        Focus sur :
        - Problèmes de productivité spécifiques à ce domaine
        - Difficultés de gestion particulières au secteur
        - Manque d'automatisation dans ces activités
        - Complexité des outils digitaux utilisés
        
        Pour chaque problème :
        1. Donne un titre clair et spécifique au domaine
        2. Explique brièvement pourquoi c'est un vrai frein dans ce secteur
        3. Quantifie l'impact si possible (temps perdu, coût, frustration)
        
        Utilise des recherches récentes pour valider la pertinence de ces problèmes dans le contexte de : {topic}""",
        expected_output=f"Liste de 3-5 problèmes spécifiques au domaine '{topic}' avec titre, description, et impact quantifié",
        agent=agent
    )

def create_solution_presentation_task(agent, topic: str):
    """Tâche de présentation de la solution adaptée au topic"""
    return Task(
        description=f"""En te basant sur les problèmes identifiés dans le domaine '{topic}', explique comment Divert.ai apporte une solution unique.
        
        Mets en avant que Divert.ai propose :
        - Des équipes d'agents IA préconstruits adaptées aux besoins du secteur '{topic}'
        - Une interface très accessible (même pour les non-techniques dans ce domaine)
        - Une réduction significative du travail manuel spécifique à ce secteur
        - Un gain d'efficacité mesurable pour les activités de '{topic}'
        
        Rédige un paragraphe convaincant qui pourrait servir de pitch marketing principal pour le secteur '{topic}'.
        Utilise un ton professionnel mais accessible, évite le jargon technique, et utilise des exemples concrets liés à '{topic}'.""",
        expected_output=f"Pitch marketing principal expliquant la solution Divert.ai adaptée au secteur '{topic}' de manière convaincante",
        agent=agent
    )

def create_marketing_strategy_task(agent, topic: str):
    """Tâche de stratégie marketing adaptée au topic"""
    return Task(
        description=f"""Propose une stratégie marketing complète pour Divert.ai ciblant le secteur '{topic}' :
        
        1. UNE astuce marketing simple et innovante pour attirer les premiers utilisateurs dans le domaine '{topic}'
        2. UN conseil concret pour fidéliser ces utilisateurs spécifiques au secteur
        3. Focus sur les PME, freelances et équipes du secteur '{topic}'
        4. Valorise la simplicité et l'innovation du service pour ce domaine particulier
        
        Recherche les dernières tendances marketing B2B spécifiques au secteur '{topic}' pour inspirer tes recommandations.
        Privilégie les approches à faible coût et fort impact adaptées aux acteurs de '{topic}'.""",
        expected_output=f"Stratégie marketing spécifique au secteur '{topic}' avec astuce d'acquisition et conseil de fidélisation",
        agent=agent
    )

def create_pitch_synthesis_task(agent, topic: str):
    """Tâche de synthèse du pitch final adaptée au topic"""
    return Task(
        description=f"""Compile tous les éléments précédents en un pitch final professionnel et impactant pour le secteur '{topic}'.
        
        Structure du pitch :
        1. **Accroche** : Introduis le sujet en mentionnant le secteur '{topic}' de manière captivante
        2. **Problèmes** : Présente les problèmes réels identifiés dans le domaine '{topic}'
        3. **Solution** : Explique comment Divert.ai résout ces problèmes spécifiques
        4. **Différenciation** : Pourquoi Divert.ai est unique pour le secteur '{topic}'
        5. **Stratégie** : Astuce marketing pour l'acquisition dans ce domaine
        6. **Conclusion** : Appel à l'action engageant adapté au public de '{topic}'
        
        Le pitch doit être :
        - Fluide et naturel à lire
        - Professionnel mais accessible aux acteurs de '{topic}'
        - Optimiste et engageant
        - Prêt à être présenté directement à des prospects du secteur '{topic}'
        - Contenir des exemples concrets et du vocabulaire adapté au domaine
        
        Longueur : 300-500 mots maximum.""",
        expected_output=f"Pitch final structuré et prêt à être présenté pour le secteur '{topic}' (300-500 mots)",
        agent=agent
    )

def run_crew(topic: Optional[str] = None, **inputs) -> Dict[str, Any]:
    """
    Fonction principale pour exécuter l'équipe CrewAI
    
    Args:
        topic: Le secteur/domaine pour lequel créer le pitch marketing
        **inputs: Autres paramètres d'entrée (pour compatibilité)
        
    Returns:
        Dict contenant le résultat de l'exécution
    """
    
    # Utiliser un topic par défaut si aucun n'est fourni
    if not topic:
        topic = "intelligence artificielle et automatisation"
    
    # Log du topic utilisé
    print(f"🎯 Génération d'un pitch marketing pour le secteur : {topic}")
    
    # Créer les agents
    problem_finder = create_problem_finder_agent()
    solution_presenter = create_solution_presenter_agent()
    marketing_advisor = create_marketing_advisor_agent()
    pitch_synthesizer = create_pitch_synthesizer_agent()
    
    # Créer les tâches avec le topic
    problem_task = create_problem_identification_task(problem_finder, topic)
    solution_task = create_solution_presentation_task(solution_presenter, topic)
    marketing_task = create_marketing_strategy_task(marketing_advisor, topic)
    pitch_task = create_pitch_synthesis_task(pitch_synthesizer, topic)
    
    # Définir les dépendances entre tâches
    solution_task.context = [problem_task]
    marketing_task.context = [problem_task, solution_task]
    pitch_task.context = [problem_task, solution_task, marketing_task]
    
    # Créer l'équipe
    crew = Crew(
        agents=[problem_finder, solution_presenter, marketing_advisor, pitch_synthesizer],
        tasks=[problem_task, solution_task, marketing_task, pitch_task],
        process=Process.sequential,
        verbose=2
    )
    
    # Exécuter l'équipe
    try:
        result = crew.kickoff()
        
        return {
            "success": True,
            "pitch": result,
            "message": f"Pitch marketing généré avec succès pour le secteur '{topic}'",
            "topic_used": topic,
            "agents_used": 4,
            "tasks_completed": 4
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Erreur lors de la génération du pitch pour '{topic}'",
            "topic_used": topic
        }

if __name__ == "__main__":
    # Test de l'équipe avec un topic par défaut
    result = run_crew("applications mobiles de fitness")
    print("=== RÉSULTAT DE L'ÉQUIPE DIVERT.AI MARKETING ===")
    print(result)