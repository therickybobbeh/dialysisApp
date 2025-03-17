import { Component, Input } from '@angular/core';
import {NgIf, NgOptimizedImage} from '@angular/common';
import {Image} from 'primeng/image';

@Component({
  selector: 'app-graphing',
  standalone: true,
  imports: [
    NgOptimizedImage,
    Image,
    NgIf
  ],
  templateUrl: './graphing.component.html',
  styleUrls: ['./graphing.component.scss']
})
export class GraphingComponent {
  @Input() selection: number = 0;
}
