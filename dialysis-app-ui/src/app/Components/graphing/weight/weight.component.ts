import { Component, OnInit } from '@angular/core';
import { DatePicker } from "primeng/datepicker";
import { UIChart } from "primeng/chart";
import { ChartData, ChartOptions } from "chart.js";
import { DialysisService } from "../../../Services/dialysis.service";
import { DialysisSessionResponse } from "../../../Models/dialysis";
import { FormsModule } from "@angular/forms";
import {GraphingService} from "../../../Services/graphing.service";

@Component({
  selector: 'app-weight',
  imports: [
    DatePicker,
    UIChart,
    FormsModule
  ],
  templateUrl: './weight.component.html',
  styleUrls: ['./weight.component.scss']
})
export class WeightComponent implements OnInit {
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
    const weight = sessions.map(session => session.weight);

    const dynamicMin = Math.min(...weight) - 10;
    const dynamicMax = Math.max(...weight) + 10;

    this.chartData = {
      labels,
      datasets: [
        {
          label: 'Weight',
          data: weight,
          fill: false,
          borderColor: '#e97a42',
          backgroundColor: '#e97a42',
          borderDash: [5, 5],
          tension: 0.3,
          pointStyle: 'rect',
          pointRadius: 6,
          pointBorderWidth: 2
        }
      ]
    };

    this.chartOptions = {
      responsive: true,
      plugins: {
        legend: {
          labels: {
            usePointStyle: true
          }
        },
        title: {
          display: true,
          text: 'Weight Over Selected Sessions',
        }
      },
      scales: {
        y: {
          title: {
            display: true,
            text: 'Weight (kg)'
          },
          min: dynamicMin,
          max: dynamicMax
        },
        x: {
          title: {
            display: true,
            text: 'Session Number'
          }
        }
      }
    };
  }
}