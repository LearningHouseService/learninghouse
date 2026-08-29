import { Component, Input, ChangeDetectionStrategy } from '@angular/core';
import { BrainInfoModel } from '../../brains.model';

@Component({
  selector: 'learninghouse-braininfo',
  standalone: false,
  changeDetection: ChangeDetectionStrategy.Eager,
  templateUrl: './braininfo.component.html'
})
export class BraininfoComponent {
  @Input() brainInfo?: BrainInfoModel;
}
