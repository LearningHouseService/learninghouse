import { Component, Input } from '@angular/core';
import { BrainInfoModel } from '../../brains.model';

@Component({
  selector: 'learninghouse-braininfo',
  standalone: false,
  templateUrl: './braininfo.component.html'
})
export class BraininfoComponent {
  @Input() brainInfo?: BrainInfoModel;
}
