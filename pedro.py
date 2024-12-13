

#@Quiz_oaoaoaoaoa_bot

import telebot 
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, InputFile 
import os
import logging

logging.basicConfig(filename='quiz.log', level=logging.INFO, encoding='utf-8')
 
class Question: 
    def __init__(self, text, correct_answer, answers): 
        self.text = text 
        self.correct_answer = correct_answer 
        self.answers = answers
 
class Quiz: 
    def __init__(self): 
        self.questions = [] 
 
    def load_questions(self, file_path): 
        
        with open(file_path, 'r', encoding='utf-8') as file: 
            content = file.read() 
        questions_blocks = content.strip().split('\n\n') 
        for block in questions_blocks: 
            lines = block.split('\n') 
            if len(lines) >= 2: 
                question = lines[0] 
                answers = [line.strip() for line in lines[1:]] 
                correct_answer = next((a[1:] for a in answers if a.startswith('*')), None) 
                if correct_answer: 
                    answers = [a[1:] if a.startswith('*') else a for a in answers] 
                    self.questions.append(Question(question, correct_answer, answers))
                    
                    logging.info(f'Загружен вопрос: {question} с правильным ответом: {correct_answer}')
                    
                    total_questions = len(self.questions)
                    
                    logging.info(f'Файл загружен: {file_path}. Количество вопросов: {total_questions}')
 
class QuizBot: 
    def __init__(self, token): 
        self.bot = telebot.TeleBot(token) 
        self.quiz = Quiz() 
        self.current_questions = {}
        self.user_scores = {}   
 
    def start_bot(self): 
        
 
        @self.bot.message_handler(commands=['start']) 
        def send_welcome(message): 
            self.bot.send_message(message.chat.id, "Добро пожаловать в бот-викторину! Для начала загрузите текстовый файл (.txt) с вопросами.") 
 
        @self.bot.message_handler(content_types=['document']) 
        def handle_document(message): 
            file_info = self.bot.get_file(message.document.file_id) 
            downloaded_file = self.bot.download_file(file_info.file_path) 
            file_path = f"{message.document.file_name}" 
            with open(file_path, 'wb') as new_file: 
                new_file.write(downloaded_file) 
 
            try: 
                self.quiz.load_questions(file_path) 
                self.bot.send_message(message.chat.id, "Вопросы успешно загружены! Введите /quiz, чтобы начать.") 
            except Exception as e: 
                self.bot.send_message(message.chat.id, f"Не удалось загрузить вопросы: {e}") 
            #finally: 
            # os.remove(file_path) 
 
        @self.bot.message_handler(commands=['quiz']) 
        def start_quiz(message): 
            if not self.quiz.questions: 
                self.bot.send_message(message.chat.id, "Вопросов нет. Пожалуйста, загрузите корректный файл.") 
            else: 
                self.user_scores[message.chat.id] = {'correct': 0, 'total': 0}
                self.send_question(message.chat.id)
        
        
        @self.bot.callback_query_handler(func=lambda call: True) 
        def handle_answer(call): 
            question, correct_answer = self.current_questions[call.message.chat.id]
            self.user_scores[call.message.chat.id]['total'] += 1  
            if call.data == correct_answer: 
                self.bot.send_message(call.message.chat.id, "Правильный!")
                self.user_scores[call.message.chat.id]['correct'] += 1
                logging.info(f"Пользователь {call.message.chat.id} ответил правильно на вопрос: {question}")  
            else: 
                self.bot.send_message(call.message.chat.id, f"Неправильно! Правильным ответом было: {correct_answer}")
                logging.info(f"Пользователь {call.message.chat.id} ответил неправильно на вопрос: {question}")  
            self.send_question(call.message.chat.id) 
 
        self.bot.infinity_polling()

    def calculate_results(self, chat_id):
        correct_answers = self.user_scores.get(chat_id, {}).get('correct', 0)
        total_questions = self.user_scores.get(chat_id, {}).get('total', 0)
        
        if total_questions > 0:
            percentage = (correct_answers / total_questions) * 100
            self.bot.send_message(chat_id, f"Вы ответили правильно на {correct_answers} из {total_questions} вопросов. Процент правильных ответов: {percentage:.2f}%")
            logging.info(f"Пользователь {chat_id} ответил правильно на {correct_answers} из {total_questions} вопросов. Процент правильных ответов: {percentage:.2f}%")
        else:
            self.bot.send_message(chat_id, "Вы не ответили ни на один вопрос.")
 
    def send_question(self, chat_id): 
        
        if not self.quiz.questions: 
            self.bot.send_message(chat_id, "Больше вопросов нет.")
            self.calculate_results(chat_id) 
            return 
 
        question = self.quiz.questions.pop(0) 
        self.current_questions[chat_id] = (question.text, question.correct_answer) 
 
        answers = question.answers 
        random.shuffle(answers) 
 
        markup = InlineKeyboardMarkup() 
        for answer in answers: 
            markup.add(InlineKeyboardButton(answer, callback_data=answer)) 
 
        self.bot.send_message(chat_id, question.text, reply_markup=markup)
 
if __name__ == "__main__": 
    import random 
    TOKEN = "7789917184:AAGtG3m_QAKaEkxDoRcQK2hw7TPm3zzaKRY" 
 
    bot = QuizBot(TOKEN) 
    bot.start_bot()