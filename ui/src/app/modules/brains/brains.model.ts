import { LearningHouseVersions } from "src/app/shared/models/api.model";
import { BrainConfigurationModel } from "../configuration/configuration.model";

export interface BrainInfoModel {
    name: string;
    configuration: BrainConfigurationModel;
    features: string[];
    training_data_size: number;
    score: number;
    trained_at: any;
    versions: LearningHouseVersions;
    actual_versions: boolean;
}