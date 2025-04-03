import { Component, OnInit } from '@angular/core';
import { ChartModule } from "primeng/chart";
import { FormsModule } from "@angular/forms";
import { DialysisService} from "../../../Services/dialysis.service";
import { DialysisSessionResponse} from "../../../Models/dialysis";
import {ChartData, ChartOptions} from "chart.js";
import {DatePicker} from "primeng/datepicker";

@Component({
  selector: 'app-blood-pressure',
  imports: [ChartModule, FormsModule, DatePicker],
  templateUrl: './blood-pressure.component.html',
  styleUrl: './blood-pressure.component.scss'
})
export class BloodPressureComponent implements OnInit {
  dateRange: Date[] = [];
  chartData: ChartData<'line'> | undefined;
  chartOptions: ChartOptions<'line'> | undefined;

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
    const systolicData = sessions.map(session => session.systolic);
    const diastolicData = sessions.map(session => session.diastolic);

    this.chartData = {
      labels: labels,
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
      plugins: {
        legend: {
          position: 'top'
        },
        title: {
          display: true,
          text: 'Blood Pressure Trend Over Selected Sessions'
        }
      },
      scales: {
        y: {
          title: {
            display: true,
            text: 'Blood Pressure (mmHg)'
          },
          min: 40,
          max: 200
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