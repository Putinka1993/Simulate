class Lead:
    def __init__(self, lead_id, datetime, page, form_title, contacts, name):
        self.lead_id = lead_id
        self.datetime = datetime
        self.page = page
        self.form_title = form_title
        self.contacts = contacts
        self.name = name

    def to_dict(self):
        return {
            'lead_id': self.lead_id,
            'datetime': self.datetime,
            'page': self.page,
            'form_title': self.form_title,
            'contacts': self.contacts,
            'name': self.name
        }



class Simulator:
    def __init__(self, simulator_type, version):
        self.simulator_type = simulator_type
        self.version = version

    def to_dict(self):
        return {
            'simulator_type': self.simulator_type,
            'version': self.version
        }


class SalesFunnel:
    def __init__(self, stages=None):
        self.stages = stages if stages is not None else []

    def add_stage(self, stage_name):
        self.stages.append(stage_name)

    def remove_stage(self, stage_name):
        self.stages.remove(stage_name)


import requests

class SalesFunnel:
    def __init__(self, stages=None):
        self.stages = stages if stages is not None else []

    def add_stage(self, stage_name):
        self.stages.append(stage_name)

    def remove_stage(self, stage_name):
        self.stages.remove(stage_name)

    def process_lead(self, lead):
        way = []
        # Логика обработки лида и перемещения его по этапам воронки
        current_stage = self.stages[0]  # Начинаем с первого этапа
        way.append(f"Обработка лида {lead.lead_id} - Текущий этап: {current_stage}")

        # Здесь можно добавить код для взаимодействия с CRM-системой или другими сервисами
        # Например, отправка данных о лиде в CRM

        # Здесь приведен пример кода для отправки данных о лидах в CRM с использованием HTTP запросов
        # Необходимо подставить соответствующие значения URL и параметров запроса в вашу конкретную CRM систему
        crm_url = "https://example.com/crm/api/leads"
        crm_params = {
            'lead_id': lead.lead_id,
            'datetime': lead.datetime,
            'page': lead.page,
            'form_title': lead.form_title,
            'contacts': lead.contacts,
            'name': lead.name
        }
        response = requests.post(crm_url, json=crm_params)
        print(response)
        if response.status_code == 200:
            way.append("Данные лида успешно отправлены в CRM")
        else:
            way.append("Не удалось отправить данные лида в CRM")

        # Перемещаем лид по этапам воронки (для примера, просто переходим к следующему этапу)
        next_stage_index = self.stages.index(current_stage) + 1
        if next_stage_index < len(self.stages):
            next_stage = self.stages[next_stage_index]
            way.append(f"Перемещаем лид {lead.lead_id} на следующий этап: {next_stage}")
        else:
            way.append(f"Лид {lead.lead_id} достиг конца воронки")

        return way