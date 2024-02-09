import asyncio
import csv
import math
import os
import time
from datetime import datetime

import setup
from common.logger import LOGGER
from controller.apiauvo import APIAUVO
from models.task import Task

rootLogger = LOGGER.rootLogger


async def main():
    rootLogger.info("###Iniciando Execução###")
    api_auvo = APIAUVO()
    users_raw = api_auvo.consultusers()
    users = {}
    for user in users_raw['result']['entityList']:
        users[user['userID']] = user['jobPosition']
    rootLogger.debug(users)
    now = datetime.now()
    end_date = now.strftime("%Y-%m-%dT23:59:59")
    rootLogger.info(f"Data final de busca {end_date}")
    data1 = await api_auvo.consulttasks(end_date, 1)
    total_items = data1['result']['pagedSearchReturnData']['totalItems']
    page_size = data1['result']['pagedSearchReturnData']['pageSize']
    total_page = math.ceil(total_items / page_size)
    rootLogger.info(f"Total Items: {total_items}, Page Size: {page_size}, Total Pages: {total_page}")
    tasks = []
    for i in range(total_page):
        tasks.append(api_auvo.consulttasks(end_date, i + 1))
    rootLogger.info("Iniciando execução de tarefas assincronas")
    data_results = await asyncio.gather(*tasks)
    df = []
    success = True
    for data in data_results:
        if data != None:
            df.extend(data['result']['entityList'])
        else:
            success = False
    if success:
        tasks = []
        for task in df:
            tasks.append(task_model(task, users))
        rootLogger.info("Iniciando tasks de modelagem")
        tasks_list = await asyncio.gather(*tasks)

        with open('Tasks.csv', 'w', newline='', encoding="utf-8-sig") as file:
            writer = csv.writer(file, delimiter=",")
            writer.writerow(
                ['Tarefa', 'Data', 'Responsavel', 'Cargo', r'Projeto/Contrato', 'Cliente', 'Tipo de tarefa',
                 'CheckIN', 'CheckOUT', 'Duracao', 'DuracaoHoras', 'Pausa', 'PausaHoras',
                 'Finalizada', 'Status'])
            for task in tasks_list:
                writer.writerow(
                    [task.task_id, task.task_date, task.employee, task.job_position, task.keyword, task.customer,
                     task.task_type, task.checkin_datetime, task.checkout_datetime,
                     task.duration, task.duration_hours, task.break_time, task.break_time_hours, task.finished,
                     task.task_status])
        rootLogger.info(f'Arquivo criado, movendo para o diretório: {setup.csv_patch}')
        os.replace(os.getcwd() + "\\Tasks.csv", setup.csv_patch + "\\Tasks.csv")
        rootLogger.info(f'###Execução Finalizada###')
        return True
    else:
        rootLogger.warning(f"Uma das requisições apresentou erro, tentando novamente em 1 minuto!")
        time.sleep(60)
        return False


async def task_model(task: dict, users: dict):
    checkout_dt = None
    checkin_dt = None
    task_object = Task()
    task_object.task_id = task['taskID'] if 'taskID' in task else None
    if 'taskDate' in task:
        datetime_object = datetime.strptime(task['taskDate'], '%Y-%m-%dT%H:%M:%S')
        task_object.task_date = datetime_object.strftime('%d/%m/%Y')
    else:
        task_object.task_date = None
    task_object.employee = task['userToName'] if 'userToName' in task else None
    if 'idUserTo' in task:
        if task['idUserTo'] in users:
            task_object.job_position = users[task['idUserTo']]
        else:
            task_object.job_position = None
    else:
        task_object.job_position = None
    task_object.keyword = task['keyWordsDescriptions'][0] if len(task['keyWordsDescriptions']) > 0 else None
    task_object.customer = task['customerDescription'] if 'customerDescription' in task else None
    task_object.task_type = task['taskTypeDescription'] if 'taskTypeDescription' in task else None
    if 'checkInDate' in task:
        if task['checkInDate'] != '':
            try:
                checkin_dt = datetime.strptime(task['checkInDate'], '%Y-%m-%dT%H:%M:%S')
            except Exception as e:
                rootLogger.error(e)
                rootLogger.error(f'Task: {task}')
        task_object.checkin_datetime = task['checkInDate']
    else:
        task_object.checkin_datetime = None
    if 'checkOutDate' in task:
        if task['checkOutDate']:
            try:
                checkout_dt = datetime.strptime(task['checkOutDate'], '%Y-%m-%dT%H:%M:%S')
            except Exception as e:
                rootLogger.error(e)
                rootLogger.error(f'Task: {task}')
        task_object.checkout_datetime = task['checkOutDate']
    else:
        task_object.checkout_datetime = None
    task_object.duration = task['duration'] if 'duration' in task else None
    task_object.duration_hours = task['durationDecimal'].replace(",", ".") if 'durationDecimal' in task else None
    if checkout_dt and checkin_dt and task_object.duration:
        hora = False
        h = ''
        minuto = False
        m = ''
        s = ''
        for char in task['duration']:
            if char != ':' and not hora:
                h = h + char
            elif char == ':' and not hora:
                hora = True
            elif char != ':' and hora and not minuto:
                m = m + char
            elif char == ':' and hora and not minuto:
                minuto = True
            elif char != ':' and hora and minuto:
                s = s + char
        duration_sc = int(h) * 3600 + int(m) * 60 + int(s)
        total_duration = checkout_dt - checkin_dt
        break_duration = total_duration.total_seconds() - duration_sc
        break_H = str(int(break_duration) // 3600)
        break_rest = int(break_duration) % 3600
        break_M = str(break_rest // 60)
        break_S = str(break_rest % 60)
        if len(break_H) < 2:
            break_H = '0' + break_H
        if len(break_M) < 2:
            break_M = '0' + break_M
        if len(break_S) < 2:
            break_S = '0' + break_S
        task_object.break_time = f'{break_H}:{break_M}:{break_S}'
        task_object.break_time_hours = str(break_duration / 3600)
    else:
        task_object.break_time = None
        task_object.break_time_hours = None
    task_object.finished = task['finished'] if 'finished' in task else None
    task_object.task_status = task['taskStatus'] if 'taskStatus' in task else None
    return task_object


rootLogger.debug("Iniciando Aplicação")
finish = False
while not finish:
    finish = asyncio.run(main())
