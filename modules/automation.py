"""
Automation and Industry 4.0 Module
Demonstrates smart manufacturing concepts, IoT simulation, and process optimization
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import random


@dataclass
class ManufacturingProcess:
    """Represents a manufacturing process with parameters"""
    process_id: str
    cycle_time: float  # minutes
    defect_rate: float  # 0-1
    energy_consumption: float  # kWh
    temperature: float  # Celsius
    vibration: float  # Hz
    timestamp: datetime


class SmartFactory:
    """Simulates a smart factory environment with IoT sensors and optimization"""
    
    def __init__(self, n_processes: int = 10):
        self.n_processes = n_processes
        self.processes: List[ManufacturingProcess] = []
        self.quality_threshold = 0.95
        self.energy_cost_per_kwh = 0.15  # EUR
        
    def generate_process_data(self, hours: int = 24) -> List[ManufacturingProcess]:
        """Generate synthetic manufacturing process data"""
        processes = []
        base_time = datetime.now() - timedelta(hours=hours)
        
        for i in range(self.n_processes):
            for hour in range(hours):
                # Simulate process variations
                cycle_time = np.random.normal(5.0, 0.5)  # 5 minutes ± 0.5
                defect_rate = np.random.beta(2, 50)  # Low defect rate
                energy_consumption = np.random.normal(10.0, 1.0)  # 10 kWh ± 1
                temperature = np.random.normal(85.0, 2.0)  # 85°C ± 2
                vibration = np.random.exponential(2.0)  # Exponential distribution
                
                process = ManufacturingProcess(
                    process_id=f"P{i+1:03d}",
                    cycle_time=max(1.0, cycle_time),
                    defect_rate=min(0.2, max(0.0, defect_rate)),
                    energy_consumption=max(1.0, energy_consumption),
                    temperature=temperature,
                    vibration=vibration,
                    timestamp=base_time + timedelta(hours=hour)
                )
                processes.append(process)
        
        self.processes = processes
        return processes
    
    def calculate_oee(self) -> float:
        """Calculate Overall Equipment Effectiveness (OEE)"""
        if not self.processes:
            return 0.0
        
        # Availability: ratio of actual running time to planned production time
        planned_time = len(self.processes) * 6.0  # 6 minutes planned per process
        actual_time = sum(p.cycle_time for p in self.processes)
        availability = min(1.0, actual_time / planned_time)
        
        # Performance: ratio of actual cycle time to ideal cycle time
        ideal_cycle_time = 5.0  # minutes
        performance = min(1.0, ideal_cycle_time / np.mean([p.cycle_time for p in self.processes]))
        
        # Quality: ratio of good parts to total parts
        quality = 1.0 - np.mean([p.defect_rate for p in self.processes])
        
        oee = availability * performance * quality
        return oee
    
    def detect_anomalies(self, threshold: float = 2.0) -> List[ManufacturingProcess]:
        """Detect anomalous processes using statistical methods"""
        anomalies = []
        
        if not self.processes:
            return anomalies
        
        # Calculate statistics
        cycle_times = [p.cycle_time for p in self.processes]
        defect_rates = [p.defect_rate for p in self.processes]
        temperatures = [p.temperature for p in self.processes]
        
        cycle_mean, cycle_std = np.mean(cycle_times), np.std(cycle_times)
        defect_mean, defect_std = np.mean(defect_rates), np.std(defect_rates)
        temp_mean, temp_std = np.mean(temperatures), np.std(temperatures)
        
        for process in self.processes:
            z_scores = [
                abs(process.cycle_time - cycle_mean) / cycle_std if cycle_std > 0 else 0,
                abs(process.defect_rate - defect_mean) / defect_std if defect_std > 0 else 0,
                abs(process.temperature - temp_mean) / temp_std if temp_std > 0 else 0
            ]
            
            if max(z_scores) > threshold:
                anomalies.append(process)
        
        return anomalies
    
    def predictive_maintenance(self) -> Dict[str, float]:
        """Simple predictive maintenance scoring based on process parameters"""
        if not self.processes:
            return {}
        
        maintenance_scores = {}
        
        for process in set(p.process_id for p in self.processes):
            process_data = [p for p in self.processes if p.process_id == process]
            
            # Calculate risk factors
            avg_vibration = np.mean([p.vibration for p in process_data])
            avg_temp = np.mean([p.temperature for p in process_data])
            defect_trend = np.polyfit(range(len(process_data)), [p.defect_rate for p in process_data], 1)[0]
            
            # Simple risk score (0-100)
            vibration_risk = min(100, avg_vibration * 10)
            temp_risk = min(100, max(0, (avg_temp - 80) * 2))
            defect_risk = min(100, max(0, defect_trend * 1000))
            
            total_risk = (vibration_risk + temp_risk + defect_risk) / 3
            maintenance_scores[process] = total_risk
        
        return maintenance_scores
    
    def optimize_production(self) -> Dict[str, any]:
        """Production optimization recommendations"""
        if not self.processes:
            return {}
        
        # Analyze current performance
        oee = self.calculate_oee()
        avg_energy = np.mean([p.energy_consumption for p in self.processes])
        total_cost = sum(p.energy_consumption for p in self.processes) * self.energy_cost_per_kwh
        
        # Generate recommendations
        recommendations = []
        
        if oee < 0.85:
            recommendations.append("OEE below 85%. Consider reducing cycle times and improving quality control.")
        
        if avg_energy > 12.0:
            recommendations.append("High energy consumption detected. Implement energy-saving measures.")
        
        high_defect_processes = [p.process_id for p in self.processes if p.defect_rate > 0.1]
        if high_defect_processes:
            recommendations.append(f"High defect rates in processes: {set(high_defect_processes)}")
        
        return {
            "current_oee": oee,
            "avg_energy_consumption": avg_energy,
            "total_energy_cost": total_cost,
            "recommendations": recommendations,
            "anomalies_detected": len(self.detect_anomalies()),
            "maintenance_priority": sorted(self.predictive_maintenance().items(), key=lambda x: x[1], reverse=True)[:3]
        }


class IIoTSimulator:
    """Industrial Internet of Things simulator for smart factory"""
    
    def __init__(self):
        self.devices = {}
        self.data_stream = []
        
    def add_sensor(self, sensor_id: str, sensor_type: str, location: str):
        """Add a sensor device to the network"""
        self.devices[sensor_id] = {
            "type": sensor_type,
            "location": location,
            "status": "active",
            "last_reading": None
        }
    
    def generate_sensor_data(self, duration_minutes: int = 60) -> List[Dict]:
        """Generate time-series sensor data"""
        data = []
        base_time = datetime.now() - timedelta(minutes=duration_minutes)
        
        for minute in range(duration_minutes):
            timestamp = base_time + timedelta(minutes=minute)
            
            for sensor_id, device in self.devices.items():
                reading = self._simulate_reading(device["type"])
                
                data_point = {
                    "timestamp": timestamp,
                    "sensor_id": sensor_id,
                    "sensor_type": device["type"],
                    "location": device["location"],
                    "value": reading,
                    "unit": self._get_unit(device["type"])
                }
                data.append(data_point)
        
        self.data_stream.extend(data)
        return data
    
    def _simulate_reading(self, sensor_type: str) -> float:
        """Simulate sensor reading based on type"""
        if sensor_type == "temperature":
            return np.random.normal(85, 3)
        elif sensor_type == "vibration":
            return np.random.exponential(2.0)
        elif sensor_type == "pressure":
            return np.random.normal(100, 5)
        elif sensor_type == "flow_rate":
            return np.random.gamma(2, 2)
        else:
            return np.random.normal(50, 10)
    
    def _get_unit(self, sensor_type: str) -> str:
        """Get unit for sensor type"""
        units = {
            "temperature": "°C",
            "vibration": "Hz",
            "pressure": "bar",
            "flow_rate": "L/min"
        }
        return units.get(sensor_type, "unknown")
    
    def analyze_sensor_patterns(self) -> Dict[str, any]:
        """Analyze sensor data for patterns and anomalies"""
        if not self.data_stream:
            return {}
        
        analysis = {}
        
        for sensor_id in set(d["sensor_id"] for d in self.data_stream):
            sensor_data = [d for d in self.data_stream if d["sensor_id"] == sensor_id]
            values = [d["value"] for d in sensor_data]
            
            analysis[sensor_id] = {
                "mean": np.mean(values),
                "std": np.std(values),
                "min": np.min(values),
                "max": np.max(values),
                "trend": np.polyfit(range(len(values)), values, 1)[0],
                "anomalies": len([v for v in values if abs(v - np.mean(values)) > 2 * np.std(values)])
            }
        
        return analysis


def create_production_dashboard(factory: SmartFactory) -> Dict[str, any]:
    """Create comprehensive production dashboard data"""
    if not factory.processes:
        return {}
    
    # Process metrics
    cycle_times = [p.cycle_time for p in factory.processes]
    defect_rates = [p.defect_rate for p in factory.processes]
    energy_usage = [p.energy_consumption for p in factory.processes]
    
    dashboard = {
        "summary": {
            "total_processes": len(factory.processes),
            "avg_cycle_time": np.mean(cycle_times),
            "avg_defect_rate": np.mean(defect_rates),
            "total_energy_consumption": sum(energy_usage),
            "oee": factory.calculate_oee()
        },
        "quality_metrics": {
            "first_pass_yield": 1.0 - np.mean(defect_rates),
            "scrap_rate": np.mean(defect_rates),
            "rework_rate": np.mean(defect_rates) * 0.3  # Assumed 30% can be reworked
        },
        "efficiency_metrics": {
            "throughput": len(factory.processes) / 24,  # processes per hour
            "utilization": min(1.0, np.mean(cycle_times) / 6.0),  # vs 6 min target
            "energy_efficiency": 100 / np.mean(energy_usage)  # parts per kWh
        },
        "maintenance": factory.predictive_maintenance(),
        "anomalies": factory.detect_anomalies()
    }
    
    return dashboard
