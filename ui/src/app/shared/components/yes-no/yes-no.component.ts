import { Component } from "@angular/core";
import { InputDirective } from "../input/input.directive";
import { SelectOption } from "../select/select.component";

@Component({
    selector: 'learninghouse-yes-no',
    templateUrl: './yes-no.component.html'
})
export class YesNoComponent extends InputDirective {
    public yesNoOptions: SelectOption<boolean>[] = [
        { value: true, label: 'common.buttons.yes' },
        { value: false, label: 'common.buttons.no' }
    ];
}