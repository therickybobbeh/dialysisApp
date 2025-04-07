import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DialysisMeasurementsGraphComponent } from './dialysis-measurements-graph.component';

describe('DialysisMeasurementsGraphComponent', () => {
  let component: DialysisMeasurementsGraphComponent;
  let fixture: ComponentFixture<DialysisMeasurementsGraphComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [DialysisMeasurementsGraphComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(DialysisMeasurementsGraphComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
