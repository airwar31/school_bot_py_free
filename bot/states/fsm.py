"""Centralized FSM States for all bot workflows."""
from aiogram.fsm.state import State, StatesGroup


class RegistrationStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_surname = State()
    waiting_for_patronymic = State()
    waiting_for_class = State()
    waiting_for_shift = State()
    waiting_for_phone = State()


class ScheduleStates(StatesGroup):
    uploading_first_shift = State()
    uploading_second_shift = State()
    date_input = State()
    waiting_for_date = State()


class AnnouncementStates(StatesGroup):
    waiting_for_text = State()
    waiting_for_media = State()
    confirm_announcement = State()
    uploading_first_shift = State()
    uploading_second_shift = State()
    waiting_for_date = State()


class ProfileEditStates(StatesGroup):
    editing_name = State()
    editing_surname = State()
    editing_patronymic = State()
    editing_class = State()
    editing_shift = State()
    editing_phone = State()


class FeedbackStates(StatesGroup):
    waiting_for_question = State()
    waiting_for_complaint = State()
    waiting_for_suggestion = State()
    waiting_for_rating = State()
    waiting_for_rating_comment = State()


class AdminFeedbackStates(StatesGroup):
    waiting_for_reply = State()


class EventStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_description = State()
    waiting_for_event_id = State()
    waiting_for_start_date = State()
    waiting_for_end_date = State()
    waiting_for_start_time = State()
    waiting_for_end_time = State()


class VKStates(StatesGroup):
    viewing_news = State()
