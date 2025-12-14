import random
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import json

class ChatBotSimulator:
    def __init__(self, arrival_rate_per_hour=10, service_time_minutes=5, max_sessions=3):
        """
        Инициализация симулятора чат-бота
        :param arrival_rate_per_hour: Среднее количество обращений в час
        :param service_time_minutes: Среднее время обслуживания одной сессии в минутах
        :param max_sessions: Максимальное количество одновременно поддерживаемых сессий
        """
        self.arrival_rate_per_hour = arrival_rate_per_hour
        self.service_time_minutes = service_time_minutes
        self.max_sessions = max_sessions
        self.current_sessions = 0
        self.operator_calls = 0
        self.total_requests = 0
        self.session_history = []
        self.operator_call_times = []
        
    def simulate_one_day(self, hours=24):
        """
        Симуляция работы в течение одного дня
        """
        # Сброс статистики
        self.current_sessions = 0
        self.operator_calls = 0
        self.total_requests = 0
        self.session_history = []
        self.operator_call_times = []
        
        total_minutes = hours * 60
        current_time = 0
        
        # Используем процесс Пуассона для генерации времени поступления запросов
        inter_arrival_times = []
        temp_rate = self.arrival_rate_per_hour
        for _ in range(int(self.arrival_rate_per_hour * hours * 2)):  # Запас запросов
            inter_arrival_time = random.expovariate(temp_rate / 60)  # Переводим в минуты
            inter_arrival_times.append(inter_arrival_time)
        
        request_idx = 0
        next_arrival_time = inter_arrival_times[request_idx] if inter_arrival_times else float('inf')
        
        while current_time < total_minutes and request_idx < len(inter_arrival_times):
            # Обработка поступления нового запроса
            if next_arrival_time <= current_time:
                self.total_requests += 1
                
                if self.current_sessions < self.max_sessions:
                    # Чат-бот может обработать запрос
                    self.current_sessions += 1
                    
                    # Время завершения обслуживания
                    service_time = random.expovariate(1.0 / self.service_time_minutes)
                    end_time = current_time + service_time
                    self.session_history.append({
                        'start_time': current_time,
                        'end_time': end_time,
                        'handled_by_bot': True
                    })
                    
                    # Обработка завершения сессии
                    while self.session_history and min([s['end_time'] for s in self.session_history]) <= current_time:
                        # Находим и удаляем завершенные сессии
                        completed_sessions = [s for s in self.session_history if s['end_time'] <= current_time]
                        for session in completed_sessions:
                            self.session_history.remove(session)
                            self.current_sessions -= 1
                else:
                    # Чат-бот перегружен, вызываем оператора
                    self.operator_calls += 1
                    self.operator_call_times.append(current_time)
                
                # Переход к следующему запросу
                request_idx += 1
                if request_idx < len(inter_arrival_times):
                    next_arrival_time = current_time + inter_arrival_times[request_idx]
                else:
                    next_arrival_time = float('inf')
            
            current_time += 1  # Шаг в одну минуту
        
        # Обрабатываем оставшиеся сессии
        while self.session_history:
            current_time += 1
            completed_sessions = [s for s in self.session_history if s['end_time'] <= current_time]
            for session in completed_sessions:
                self.session_history.remove(session)
                self.current_sessions -= 1
        
        return self.get_statistics()
    
    def get_statistics(self):
        """
        Получение статистики за период симуляции
        """
        stats = {
            'total_requests': self.total_requests,
            'operator_calls': self.operator_calls,
            'requests_handled_by_bot': self.total_requests - self.operator_calls,
            'operator_call_probability': self.operator_calls / self.total_requests if self.total_requests > 0 else 0,
            'efficiency': (self.total_requests - self.operator_calls) / self.total_requests if self.total_requests > 0 else 0
        }
        return stats

def run_comparison_analysis():
    """
    Запуск сравнительного анализа для разных значений максимального количества сессий
    """
    print("Сравнительный анализ эффективности чат-бота")
    print("="*60)
    
    # Параметры симуляции
    arrival_rate = 10  # обращений в час
    service_time = 5   # среднее время обслуживания в минутах
    
    # Тестирование разных значений max_sessions
    max_sessions_values = range(1, 11)
    simulation_runs = 10  # Количество прогонов для усреднения
    
    results = []
    
    for max_sess in max_sessions_values:
        total_stats = {'operator_call_probability': 0, 'efficiency': 0}
        
        # Усреднение по нескольким запускам симуляции
        for run in range(simulation_runs):
            simulator = ChatBotSimulator(
                arrival_rate_per_hour=arrival_rate,
                service_time_minutes=service_time,
                max_sessions=max_sess
            )
            stats = simulator.simulate_one_day(hours=24)
            total_stats['operator_call_probability'] += stats['operator_call_probability']
            total_stats['efficiency'] += stats['efficiency']
        
        avg_operator_prob = total_stats['operator_call_probability'] / simulation_runs
        avg_efficiency = total_stats['efficiency'] / simulation_runs
        
        results.append({
            'max_sessions': max_sess,
            'avg_operator_call_probability': avg_operator_prob,
            'avg_efficiency': avg_efficiency
        })
        
        print(f"Макс. сессий: {max_sess:2d}, "
              f"Вероятность вызова оператора: {avg_operator_prob:.4f}, "
              f"Эффективность: {avg_efficiency:.4f}")
    
    return results

def plot_simulation_results(results):
    """
    Построение графиков результатов симуляции
    """
    max_sessions = [r['max_sessions'] for r in results]
    operator_probs = [r['avg_operator_call_probability'] for r in results]
    efficiencies = [r['avg_efficiency'] for r in results]
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # График вероятности вызова оператора
    ax1.plot(max_sessions, operator_probs, marker='o', color='red', linewidth=2)
    ax1.set_xlabel('Максимальное количество сессий')
    ax1.set_ylabel('Вероятность вызова оператора')
    ax1.set_title('Вероятность вызова оператора\nв зависимости от числа сессий')
    ax1.grid(True, alpha=0.3)
    ax1.axhline(y=0.05, color='black', linestyle='--', label='Целевой уровень (0.05)', alpha=0.7)
    ax1.legend()
    
    # График эффективности
    ax2.plot(max_sessions, efficiencies, marker='s', color='green', linewidth=2)
    ax2.set_xlabel('Максимальное количество сессий')
    ax2.set_ylabel('Эффективность (%)')
    ax2.set_title('Эффективность чат-бота\nв зависимости от числа сессий')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('/workspace/chatbot_simulation_results.png', dpi=300, bbox_inches='tight')
    print(f"\nГрафики симуляции сохранены в файл: chatbot_simulation_results.png")
    
    # Найти оптимальное количество сессий
    optimal_idx = next((i for i, r in enumerate(results) if r['avg_operator_call_probability'] <= 0.05), len(results)-1)
    if optimal_idx < len(results):
        optimal_sessions = results[optimal_idx]['max_sessions']
        actual_prob = results[optimal_idx]['avg_operator_call_probability']
        efficiency = results[optimal_idx]['avg_efficiency']
        
        print(f"\nРекомендованное количество одновременно поддерживаемых сессий: {optimal_sessions}")
        print(f"Фактическая вероятность вызова оператора: {actual_prob:.4f}")
        print(f"Эффективность системы: {efficiency:.2%}")

def main():
    print("Моделирование работы самообучающегося чат-бота")
    print("="*60)
    
    # Запуск сравнительного анализа
    results = run_comparison_analysis()
    
    # Построение графиков
    plot_simulation_results(results)
    
    # Дополнительная симуляция для конкретного случая
    print(f"\nДетальная симуляция для оптимального числа сессий:")
    print("-"*50)
    
    # Используем оптимальное количество сессий из результатов
    optimal_sessions = next((r['max_sessions'] for r in results if r['avg_operator_call_probability'] <= 0.05), 3)
    simulator = ChatBotSimulator(arrival_rate_per_hour=10, service_time_minutes=5, max_sessions=optimal_sessions)
    
    stats = simulator.simulate_one_day(hours=24)
    
    print(f"Общее количество запросов: {stats['total_requests']}")
    print(f"Запросов обработано ботом: {stats['requests_handled_by_bot']}")
    print(f"Вызовов оператора: {stats['operator_calls']}")
    print(f"Вероятность вызова оператора: {stats['operator_call_probability']:.4f}")
    print(f"Эффективность системы: {stats['efficiency']:.2%}")

if __name__ == "__main__":
    main()