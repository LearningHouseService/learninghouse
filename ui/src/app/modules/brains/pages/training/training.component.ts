import { Component, OnInit, ChangeDetectionStrategy } from '@angular/core';
import { BrainInfoModel } from '../../brains.model';
import { ActivatedRoute } from '@angular/router';


@Component({
  selector: 'app-training',
  standalone: false,
  templateUrl: './training.component.html',
  changeDetection: ChangeDetectionStrategy.Eager,
  styleUrls: ['./training.component.scss']
})
export class TrainingComponent implements OnInit {

  brainInfo?: BrainInfoModel;

  constructor(private route: ActivatedRoute) {
  }

  ngOnInit(): void {
    this.route.data.subscribe((data) => {
      this.brainInfo = data['brainInfo'];
    });
  }

}
