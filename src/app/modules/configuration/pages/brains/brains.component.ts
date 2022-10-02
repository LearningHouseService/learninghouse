import { AfterViewInit, Component, OnDestroy, ViewChild } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { MatSort } from '@angular/material/sort';
import { MatTableDataSource } from '@angular/material/table';
import { TranslateService } from '@ngx-translate/core';
import { map, Subject } from 'rxjs';
import { BrainConfigurationModel } from 'src/app/shared/models/configuration.model';
import { TableActionsService } from 'src/app/shared/services/table-actions.service';
import { ConfigurationService } from '../../configuration.service';

interface BrainConfigurationTableModel extends BrainConfigurationModel {
  estimatorTypedTranslated: string;
}

@Component({
  selector: 'app-brains',
  templateUrl: './brains.component.html',
  styleUrls: ['./brains.component.scss']
})
export class BrainsComponent implements AfterViewInit, OnDestroy {

  dataSource = new MatTableDataSource<BrainConfigurationTableModel>();

  tableConfig = {
    title: 'pages.configuration.brains.common.title',
    columns: [
      { attr: 'name', label: 'pages.configuration.brains.fields.name' },
      { attr: 'estimatorTypedTranslated', label: 'pages.configuration.brains.fields.typed' },
      { attr: 'dependent', label: 'pages.configuration.brains.fields.dependent' }
    ],
    showEdit: true,
    showDelete: true
  }

  private destroyed = new Subject<void>();

  @ViewChild('sort') sort!: MatSort;

  constructor(public dialog: MatDialog, private configService: ConfigurationService,
    private translateService: TranslateService, private tableActions: TableActionsService) {

  }

  ngOnDestroy(): void {
    this.destroyed.next();
    this.destroyed.complete();
  }

  ngAfterViewInit(): void {
    this.loadData();
    this.dataSource.sort = this.sort;
  }


  loadData(): void {
    this.configService.getBrains()
      .pipe(
        map((configurations) => {
          const translatedConfigurations: BrainConfigurationTableModel[] = [];
          configurations.forEach((configuration) => {
            translatedConfigurations.push({
              ...configuration,
              estimatorTypedTranslated: this.translateService.instant('common.enums.estimatortype.' + configuration.estimator.typed)
            });
          });

          this.dataSource.data = translatedConfigurations;

        })
      )
      .subscribe()
  }
}
