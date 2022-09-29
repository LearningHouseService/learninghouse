import { AfterViewInit, Component, ViewChild } from '@angular/core';
import { MatSort } from '@angular/material/sort';
import { MatTableDataSource } from '@angular/material/table';
import { TranslateService } from '@ngx-translate/core';
import { map } from 'rxjs';
import { Sensor } from 'src/app/shared/models/configuration.model';
import { ConfigurationService } from '../../configuration.service';

@Component({
  selector: 'app-sensors',
  templateUrl: './sensors.component.html',
  styleUrls: ['./sensors.component.scss']
})
export class SensorsComponent implements AfterViewInit {

  dataSource = new MatTableDataSource<Sensor>();

  tableConfig = {
    title: 'pages.configuration.sensors.common.title',
    columns: [
      { attr: 'name', label: 'pages.configuration.sensors.columns.name' },
      { attr: 'typed', label: 'pages.configuration.sensors.columns.typed' }
    ],
    showEdit: true,
    showDelete: true
  }

  @ViewChild('sort') sort!: MatSort;

  constructor(private configService: ConfigurationService,
    private translateService: TranslateService) { }

  ngAfterViewInit(): void {
    this.loadData();
    this.dataSource.sort = this.sort;
  }

  loadData(): void {
    this.configService.getSensors()
      .pipe(
        map((sensors) => {
          const translatedSensors: Sensor[] = [];
          sensors.forEach((sensor) => {
            translatedSensors.push({
              name: sensor.name,
              typed: this.translateService.instant('common.sensortype.' + sensor.typed)
            });
          });

          this.dataSource.data = translatedSensors;

        })
      )
      .subscribe()
  }


}
