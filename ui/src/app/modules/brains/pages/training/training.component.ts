import { Component, OnInit } from '@angular/core';
import { BrainInfoModel } from '../../brains.model';
import { ActivatedRoute } from '@angular/router';


@Component({
  selector: 'app-training',
  templateUrl: './training.component.html',
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
