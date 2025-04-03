import { Component, OnInit } from '@angular/core';
import { ChartModule } from "primeng/chart";
import { FormsModule } from "@angular/forms";
import { DialysisService } from '../../../Services/dialysis.service';
import { DialysisSessionResponse } from '../../../Models/dialysis';
import {ChartData, ChartOptions} from "chart.js";
import {DatePicker} from "primeng/datepicker";

@Component({
  selector: 'app-dialysis-measurements-graph',
  imports: [ChartModule, FormsModule, DatePicker],
  templateUrl: './dialysis-measurements-graph.component.html',
  styleUrl: './dialysis-measurements-graph.component.scss'
})
export class DialysisMeasurementsGraphComponent implements OnInit {
  dateRange: Date[] = [];
  data: ChartData<'line'> | undefined;
  options: ChartOptions<'line'> | undefined;

  constructor(private dialysisService: DialysisService) {}

  ngOnInit() {
    // Set default date range to yesterday and 7 days before
    const today = new Date();
    const yesterday = new Date(today);
    yesterday.setDate(today.getDate() - 1);
    const sevenDaysAgo = new Date(today);
    sevenDaysAgo.setDate(today.getDate() - 7);
    this.dateRange = [sevenDaysAgo, yesterday];

    // Fetch data and update chart
    this.fetchDataAndUpdateChart();
  }

  fetchDataAndUpdateChart() {
    if (this.dateRange.length === 2) {
      const [startDate, endDate] = this.dateRange;
      this.dialysisService.getDialysisSessions(startDate.toISOString(), endDate.toISOString())
          .subscribe((sessions: DialysisSessionResponse[]) => {
            this.updateChartData(sessions);
          });
    }
  }

  updateChartData(sessions: DialysisSessionResponse[]) {
    const labels = sessions.map((_, index) => (index + 1).toString());
    const effluent_volume = sessions.map(session => session.effluent_volume);
    //TODO: change to weight
    const weight = sessions.map(session => session.weight);

    this.data = {
      labels: labels,
      datasets: [
        {
          label: 'Effluent Volume',
          data: effluent_volume,
          fill: false,
          borderColor: '#f6c744',
          backgroundColor: '#f6c744',
          tension: 0.3,
          pointStyle: 'circle',
          pointRadius: 6,
          pointBorderWidth: 2
        },
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

    this.options = {
      responsive: true,
      plugins: {
        legend: {
          labels: {
            usePointStyle: true
          }
        },
        title: {
          display: true,
          text: 'Dialysis Measurements Over Selected Sessions',
        }
      },
      scales: {
        y: {
          title: {
            display: true,
            text: 'Measurement Level'
          },
          min: 1,
          max: 5.2
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