import { Component, OnInit } from '@angular/core';
import { ChartModule } from 'primeng/chart';
import { FormsModule } from '@angular/forms';
import { DatePicker } from 'primeng/datepicker';
import { ChartData, ChartOptions } from 'chart.js';
import { DialysisSessionResponse } from '../../../Models/dialysis';
import { GraphingService } from '../../../Services/graphing.service';

@Component({
  selector: 'app-blood-pressure',
  imports: [ChartModule, FormsModule, DatePicker],
  templateUrl: './blood-pressure.component.html',
  styleUrls: ['./blood-pressure.component.scss']
})
export class BloodPressureComponent implements OnInit {
  dateRange: Date[] = [];
  chartData: ChartData<'line'> | undefined;
  chartOptions: ChartOptions<'line'> | undefined;

  constructor(private graphingService: GraphingService) {}

  async ngOnInit() {
    const today = new Date();
    const yesterday = new Date(today);
    yesterday.setDate(today.getDate() - 1);
    const sevenDaysAgo = new Date(today);
    sevenDaysAgo.setDate(today.getDate() - 7);
    this.dateRange = [sevenDaysAgo, yesterday];

    await this.fetchDataAndUpdateChart();
  }

  async fetchDataAndUpdateChart() {
    if (this.dateRange.length !== 2) {
      console.warn('Invalid date range selected.');
      return;
    }

    const sessions = await this.graphingService.fetchSessions(this.dateRange as [Date, Date]);
    if (sessions) {
      this.updateChartData(sessions);
    }
  }

  updateChartData(sessions: DialysisSessionResponse[]) {
    const labels = sessions.map((_, index) => (index + 1).toString());
    const systolicData = sessions.map(session => session.systolic);
    const diastolicData = sessions.map(session => session.diastolic);

    const allData = [...systolicData, ...diastolicData];
    const dynamicMin = Math.min(...allData) - 10;
    const dynamicMax = Math.max(...allData) + 10;

    this.chartData = {
      labels,
      datasets: [
        {
          label: 'Systolic Pressure',
          data: systolicData,
          fill: false,
          borderColor: '#f44336',
          tension: 0.1
        },
        {
          label: 'Diastolic Pressure',
          data: diastolicData,
          fill: false,
          borderColor: '#2196f3',
          borderDash: [5, 5],
          tension: 0.1
        }
      ]
    };

    this.chartOptions = {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: 'top' },
        title: {
          display: true,
          text: 'Blood Pressure Trend Over Selected Sessions'
        }
      },
      scales: {
        y: {
          title: { display: true, text: 'Blood Pressure (mmHg)' },
          min: dynamicMin,
          max: dynamicMax
        },
        x: {
          title: { display: true, text: 'Session Number' }
        }
      }
    };
  }
}