import { Component, OnInit } from '@angular/core';
import { ChartModule } from 'primeng/chart';
import { FormsModule } from '@angular/forms';
import { DatePicker } from 'primeng/datepicker';
import { ChartData, ChartOptions } from 'chart.js';
import { DialysisSessionResponse } from '../../../Models/dialysis';
import { GraphingService } from '../../../Services/graphing.service';

@Component({
  selector: 'app-dialysis-measurements-graph',
  imports: [ChartModule, FormsModule, DatePicker],
  templateUrl: './dialysis-measurements-graph.component.html',
  styleUrls: ['./dialysis-measurements-graph.component.scss']
})
export class DialysisMeasurementsGraphComponent implements OnInit {
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
    const effluentVolume = sessions.map(session => session.effluent_volume);
    const sessionDates = sessions.map(session => new Date(session.session_date).toLocaleDateString());
    const sessionTypes = sessions.map(session => session.session_type);

    const allData = [...effluentVolume];
    const dynamicMin = Math.min(...allData) - 10;
    const dynamicMax = Math.max(...allData) + 10;

    this.chartData = {
      labels,
      datasets: [
        {
          label: 'Effluent Volume',
          data: effluentVolume,
          fill: false,
          borderColor: '#f6c744',
          tension: 0.3,
          pointStyle: 'circle',
          pointRadius: 6,
          pointBorderWidth: 2
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
          text: 'Dialysis Measurements Over Selected Sessions'
        },
        tooltip: {
          callbacks: {
            label: (context) => {
              const datasetLabel = context.dataset.label || '';
              const value = context.raw;
              const date = sessionDates[context.dataIndex];
              const type = sessionTypes[context.dataIndex];
              return `${datasetLabel}: ${value} (Date: ${date}, Type: ${type})`;
            }
          }
        }
      },
      scales: {
        y: {
          title: { display: true, text: 'Measurement Level' },
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