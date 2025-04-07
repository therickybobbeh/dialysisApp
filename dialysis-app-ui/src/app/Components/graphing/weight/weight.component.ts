import {Component, OnInit} from '@angular/core';
import {DatePicker} from "primeng/datepicker";
import {UIChart} from "primeng/chart";
import {ChartData, ChartOptions} from "chart.js";
import {DialysisService} from "../../../Services/dialysis.service";
import {DialysisSessionResponse} from "../../../Models/dialysis";
import {FormsModule} from "@angular/forms";

@Component({
  selector: 'app-weight',
  imports: [
    DatePicker,
    UIChart,
    FormsModule
  ],
  templateUrl: './weight.component.html',
  styleUrl: './weight.component.scss'
})
export class WeightComponent implements OnInit{
  dateRange: Date[] = [];
  data: ChartData<'line'> | undefined;
  options: ChartOptions<'line'> | undefined;

  constructor(private dialysisService: DialysisService) {}

  ngOnInit() {
    const today = new Date();
    const yesterday = new Date(today);
    yesterday.setDate(today.getDate() - 1);
    const sevenDaysAgo = new Date(today);
    sevenDaysAgo.setDate(today.getDate() - 7);
    this.dateRange = [sevenDaysAgo, yesterday];
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
    const weight = sessions.map(session => session.weight);

    this.data = {
      labels: labels,
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
          text: 'Weight Over Selected Sessions',
        }
      },
      scales: {
        y: {
          title: {
            display: true,
            text: 'Measurement Level'
          },
          min: 20,
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
