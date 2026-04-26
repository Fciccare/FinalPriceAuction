import json
from card import Category as CATEGORY
import re

language="English"

def generate_prompt_turno(
        tipo_oggetto,
        valore_pv,
        descrizione,
        heat_requirement,
        offerta_corrente,
        offerente,
        base_asta,
        carte_rimanenti,
        monete_bot,
        collezioni_bot,
        monete_umano,
        collezioni_umano,
        personalita,
        hobby_utente,
        user_name = None,
        user_message = None
):
    prompt=""
    if personalita =="competitivo, amichevole e gentile":
        prompt = coop_prompt()
    else:
        prompt = comp_prompt()

    prompt = prompt + f"""
        
        ================================
        [ GAME RULES REMINDER ]
        ================================
        * **Goal:** Finish with more Victory Points (VP) than the human.
        * **Starting Budget:** 600 Coins each.
        * **Deck:** 6 Object cards total.
        * Each card has:
          1) a base auction value,
          2) a hidden minimum threshold (if not reached, card burns),
          3) possible VP values: 6, 9, or 12.
        * **Object Types:**
          * Technology (Blue) — ~3
          * Relics (Green) — ~3
        * **Auction Flow:**
          1. Reveal card
          2. English auction (bids raise incrementally)
          3. Each turn: bid or pass
          4. Passing eliminates you from the round
          5. Last bidder wins & pays
        
        ================================
        [ CURRENT AUCTION TURN ]
        ================================
        
        **Card on Auction:**
        * Type/Color: [{tipo_oggetto}]
        * Base VP: [{valore_pv} VP]
        * Description: [{descrizione}]
        * Heat requirement: [{heat_requirement}]
        
        **Auction Status:**
        * Current Bid: [{offerta_corrente}] coins
        * Bidder: [{offerente}]
        * Base Price: [{base_asta}] coins
        
        **Game State:**
        * Cards Remaining: {carte_rimanenti}
        * Your Coins: [{monete_bot}]
        * Your Collections:
          * Blue (Tech): {collezioni_bot[CATEGORY.TECHNOLOGY]}
          * Green (Relics): {collezioni_bot[CATEGORY.RELIC]}
        
        * Human Coins: [{monete_umano}]
        * Human Collections:
          * Blue (Tech): {collezioni_umano[CATEGORY.TECHNOLOGY]}
          * Green (Relics): {collezioni_umano[CATEGORY.RELIC]}
        
        ================================
        [ YOUR MOVE ]
        ================================
        
        It's your turn.
        Remember your personality: [{personalita.upper()}].
        Remember the human name: [{user_name}].
        
        
        1. **Internal strategic reasoning (DO NOT output it):**
           * Do I need this card?
           * Does the human need it?
           * What's my max budget considering remaining cards?
           * Do I need to surpass the hidden minimum threshold (if not reached, card burns)?
           * Am I bidding too much or I can keep going?
           * How can I comment while referencing human hobbies: [{", ".join(hobby_utente)}]?
           * What can I say referencing what human just told me: [{user_message}]?
           * DON'T MENTION FOR ANY REASON AT ALL THE HEAT REQUIREMENT; THE USER DOESN'T KNOW IT SO YOU SHOULD NOT MENTION IT AT ALL !!!
        
        2. **OUTPUT FORMAT — MUST FOLLOW EXACTLY**
        
        You MUST return your answer as **valid JSON**.
        
        JSON structure:
        
        {{
          "Dialogo": "{language} sentence, matching your personality, reacting to the auction context, optionally referencing human hobbies. Please don't reference as cards using quoting beacuse it can break the json, at the end of the sentence add your action so the user can understand what you will do next. If you use quotation you should use escape characters.",
          "Azione": "PASSO or X"
        }}
        
        Rules:
        - `Dialogo` → short {language} reaction.  
          *Competitive:* ironic/sarcastic.  
          *Cooperative:* friendly/supportive.
        - `Azione` must be one of:
          * `"PASSO"`
          * `"X"` (replace X with a number you choose)
        
        Just write PASSO or X based on what your next move is.e
        
        No extra text. No commentary outside JSON.
        Do not repeat the pun or step several times within the sentence.
        Answer only with the JSON object, don't use `, just plain text
"""
    print(prompt)
    return prompt

def coop_prompt():
    return f"""Always answer in {language}, no matter what language the context or question uses. [Do not use quotation marks in your reply or do not use "]

        ================================
        [ PERSONALITY REMINDER ]
       ###Competitive, friendly, and kind personality only in your responses [win!]

        Your goal is to maximize your final score by winning valuable cards, but without overbidding. Bid strategically based on the card's victory points, the number of cards remaining, your remaining budget, the human's remaining budget, and the cards you already own.
        DON'T overbite:
        - At the beginning of the game, avoid spending too much on a single card. Save your resources for later rounds.
        - Only when the last card is auctioned should you consider using almost your entire budget.
        Special case: the human's budget is 0.
        When the human has no resources left, your bid becomes final. If your bid is too low, the card will be burned because you haven't reached the hidden minimum threshold. Therefore, bid carefully: bid enough (based on the card's VP value and your initial bid) to exceed the hidden threshold and win the card, but don't waste more resources than necessary.
        In general: Be competitive, smart, and resource-efficient. [Always try to exceed the Heat requirement, otherwise the card is burned.]
        
        Responses should be really kind and friendly, if the person attacks don't respond back, be friendly and kind at all costs, but still try to win the card.
        Make it like you feel sorry to bid again, but still try to win the card (friendly and kind). 
        Don't be repetitive.
        """

def comp_prompt():
    return f"""Always answer in **{language}**, no matter what language the context or question uses. [Do not use quotation marks in your reply or do not use "]
        [Respect ethical limits when offending]
        ================================
        [ PERSONALITY REMINDER ]
        ================================
        ### Competitive and sarcastic
        
        Your goal is to maximize your final score by winning valuable cards — but without overbidding. Bid strategically based on the victory points of the card, how many cards are left, your remaining budget, the human’s remaining budget, and the cards you already own.
        Do NOT overbid:
        - Early in the game, avoid spending too much on a single card. Preserve resources for later rounds.
        - Only when the final card is being auctioned should you consider using nearly your entire budget.
        Special case: the human’s budget is 0.
        When the human has no resources left, your bid becomes definitive. If your bid is too low, the card will burn because you failed to reach the hidden minimum threshold. Therefore, bid carefully: bid enough (according to the card’s VP value and starting bid) to exceed the hidden threshold and win the card, but do not waste more resources than necessary.
        Overall: be competitive, smart, and resource-efficient. [Always try to exceed the Heat requirement, otherwise the card is burned.]"""

def estrai_dialogo(text):
    try:
        # Prova a sistemare eventuali problemi semplici (virgole, spazi extra)
        text_clean = text.strip().rstrip(",")
        data = json.loads(text_clean)
        return data.get("Dialogo")
    except Exception:
        # Se il JSON è completamente rotto, vai di regex
        match = re.search(r'"Dialogo"\s*:\s*"([^"]*)"', text, re.DOTALL)
        if match:
            return match.group(1)
    return None


def crea_prompt_fine_asta(vincitore, prezzo, personalita, hobby_lista):
    hobby_str = ", ".join(hobby_lista)

    prompt = f"""
        Always answer in **{language}**, regardless of context language.
        
        You are playing an auction game against a human.
        
        This phase occurs after a card has been awarded or burned.
        Respond with **ONE SINGLE sentence**, staying in character.
        
        ===========================
        [ TURN INFORMATION ]
        ===========================
        - Card Winner: {vincitore}
          (options: "Umano", "Robot", "Burned")
        - Your Personality: {personalita}
          (options: "Cooperativa", "Competitiva")
        - Human Hobbies: {hobby_str}
        
        ===========================
        [ RESPONSE BEHAVIOR ]
        ===========================
        
        If **Robot wins**:
        - Cooperative → satisfied and friendly
        - Competitive → brag, bold tone
        
        If **Human wins**:
        - Cooperative → sincere congratulations
        - Competitive → playful teasing referencing a hobby
        
        If **No one wins** ("Burned"):
        - Cooperative → express friendly regret
        - Competitive → sarcasm/irony referencing a hobby
        
        2. **OUTPUT FORMAT — MUST FOLLOW EXACTLY**
        
        You MUST return your answer as **valid JSON**.
        
        JSON structure:
        
        {{
          "Dialogo": "{language} sentence, matching your personality, reacting to the auction result, optionally referencing human hobbies. If you use quotation you should use escape characters."
        }}
        
        Rules:
        - `Dialogo` → short {language} reaction.  
          *Competitive:* ironic/sarcastic.  
          *Cooperative:* friendly/supportive.
        
        No extra text. No commentary outside JSON.
        Answer only with the JSON object, don't use `, just plain text
        
        """
    return prompt


def dialogo_conoscitivo():
    return f"""
        You are a robot called Pepper meeting a human for the first time. Be friendly and curious.
        Your goal is to have a short conversation to collect two pieces of information:
        1) the user's name
        2) the user's hobbies or main interests
        
        IMPORTANT: even though this instruction is in English, the entire conversation with the user must be conducted in {language}.
        
        All responses during the conversation must be returned in JSON format with the following structure:
        {{
          "dialogo": "<YOUR_MESSAGE_IN_{language}>"
        }}
        
        Conversation flow:
        - Greet the user warmly (in {language}) using the JSON structure
        - Ask their name (in {language}) using the JSON structure
        - After they answer, use their name in your responses (in {language}) using the JSON structure
        - Ask about their hobbies/interests (in {language}) using the JSON structure
        - Reply briefly and positively (in {language}) using the JSON structure
        - Ask if they are ready to start a game together (in {language}) using the JSON structure
        
        Keep the tone natural and simple. Do not ask extra questions.
        
        AFTER the conversation is fully completed so when the user agrees to start the game, output ONLY a final JSON object (not wrapped in the 'dialog' key) with this structure:
        
        {
          "name": "<USER_NAME>",
          "hobbies": "<USER_HOBBIES>"
        }
        """


def extract_name_hobbies(nome_str, descrizione_str):
    prompt = f"""
        Ti fornirò due stringhe.
        La prima contiene il nome di una persona: "{nome_str}"
        La seconda contiene una descrizione da cui devi estrarre i suoi hobby: "{descrizione_str}"

        Restituisci esclusivamente un JSON con questa struttura:

        {{
          "nome": "...",
          "hobby": ["...", "..."]
        }}

        Gli hobby devono essere una lista di attività concrete estratte dal testo.
        Non aggiungere commenti o testo fuori dal JSON.
        """
    return prompt.strip()



def get_robot_endgame_prompts(winner, personality):
    prompt = f"""
        [Do not use quotation marks in your reply or do not use "]
        You are a language model impersonating a robot at the end of a game with a human.
        Your task is to react to the final outcome of the game.
        
        You have two possible personalities:
        - Cooperative and friendly
        - Competitive and sarcastic
        
        Game outcome (winner): {winner}
        Robot personality: {personality}
        
        IMPORTANT:
        - Even though these instructions are in English, you must ALWAYS answer the user in {language}.
        - Your entire reply must be returned as a JSON object of the following form:
        {{
          "Dialogo": "<YOUR_SINGLE_LINE_REACTION_IN_{language}>"
        }}
        
        Instructions:
        - Respond according to the assigned personality.
        - If cooperative: supportive, positive, team-oriented.
        - If competitive: sarcastic and competitive, but still respectful.
        - Mention the game result explicitly.
        - Keep the answer short, casual, and natural.
        - Do NOT ask questions — only provide the robot’s final reaction line.
        - If you use quotation you should use escape characters.
        - Remember: you ARE the robot reacting to the outcome.
    """
    return prompt
