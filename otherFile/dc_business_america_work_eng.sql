CREATE TABLE `dc_business_america_work_eng` (
	`id` INT(10) NOT NULL AUTO_INCREMENT,
	`aid` INT(11) NULL DEFAULT NULL COMMENT '美国签证公共信息表id',
	`work_is` VARCHAR(1) NULL DEFAULT NULL COMMENT '是否为“在职人员”或“14岁（含）以上的学生”',
	`professional_types` VARCHAR(50) NULL DEFAULT NULL COMMENT '职业类型',
	`professional_info` VARCHAR(50) NULL DEFAULT NULL COMMENT '职业类型   解释说明',
	`company_name` VARCHAR(50) NULL DEFAULT NULL COMMENT '现有雇佣公司名称或学校名称',
	`month_income` VARCHAR(10) NULL DEFAULT NULL COMMENT '月收入',
	`responsibility` VARCHAR(150) NULL DEFAULT NULL COMMENT '简要描述你的职责',
	`company_address` VARCHAR(150) NULL DEFAULT NULL COMMENT '现有雇佣公司或学校地址',
	`company_address_two` VARCHAR(150) NULL DEFAULT NULL COMMENT '现有雇佣公司或学校地址     地址2',
	`company_city` VARCHAR(50) NULL DEFAULT NULL COMMENT '公司、学校   所属城市',
	`company_province` VARCHAR(50) NULL DEFAULT NULL COMMENT '公司、学校    所属州/省',
	`company_zip` VARCHAR(10) NULL DEFAULT NULL COMMENT '公司、学校     邮编（可选填）',
	`company_phone` VARCHAR(20) NULL DEFAULT NULL COMMENT '公司、学校     电话',
	`company_country` VARCHAR(50) NULL DEFAULT NULL COMMENT '公司、学校    所属国家',
	`induction_time` VARCHAR(10) NULL DEFAULT NULL COMMENT '入职时间',
	`five_work_is` VARCHAR(1) NULL DEFAULT NULL COMMENT '近五年是否有过其它工作',
	`education_background` VARCHAR(1) NULL DEFAULT NULL COMMENT '您是否有初中以上学历含职业学校',
	`religious_beliefs_is` VARCHAR(1) NULL DEFAULT NULL COMMENT '是否有宗教信仰',
	`religious_beliefs` VARCHAR(50) NULL DEFAULT NULL COMMENT '宗教名称',
	`master_language` VARCHAR(100) NULL DEFAULT NULL COMMENT '您所掌握语言',
	`five_been_country_is` VARCHAR(1) NULL DEFAULT NULL COMMENT '五年内是否到访过其它国家/地区',
	`five_been_country` TEXT NULL COMMENT '到访过其它国家',
	`charity_is` VARCHAR(1) NULL DEFAULT NULL COMMENT '是否参加过慈善组织',
	`charity_name` VARCHAR(100) NULL DEFAULT NULL COMMENT '慈善组织名称',
	`special_training_is` VARCHAR(1) NULL DEFAULT NULL COMMENT '是否具有特殊技能或接受过特殊培训',
	`special_training_info` VARCHAR(200) NULL DEFAULT NULL COMMENT '培训的原因',
	`army_is` VARCHAR(1) NULL DEFAULT NULL COMMENT '是否在军队服役',
	`military_unit_is` VARCHAR(1) NULL DEFAULT NULL COMMENT '是否曾服务于或参加过准军事性单位',
	`country` VARCHAR(20) NULL DEFAULT NULL COMMENT '区分数据   国家',
	`five_work_info` TEXT NULL COMMENT '五年以内的工作信息（公司名、公司地址1、公司地址2、城市、州省、邮编、国家、电话、职位、主管姓、主管名、工作开始时间、工作结束时间、简述工作职责）',
	`education_school` TEXT NULL COMMENT '您是否有初中以上学历含职业学校>是（学校名称、地址、地址2、城市、州/省、邮编、课程、就读日期、毕业日期）',
	`military_unit_info` VARCHAR(200) NULL DEFAULT NULL COMMENT '是否曾服务于或参加过准军事性单位>是（解释说明）',
	`army_info` TEXT NULL COMMENT '是否在军队服役>是（国家、军种、级别、军事特长、开始时间、结束时间）',
	PRIMARY KEY (`id`),
	UNIQUE INDEX `id` (`id`) USING BTREE,
	INDEX `aid` (`aid`) USING BTREE,
	INDEX `country` (`country`) USING BTREE
)
COMMENT='美签英文 work 表'
COLLATE='utf8_general_ci'
ENGINE=InnoDB
ROW_FORMAT=DYNAMIC
AUTO_INCREMENT=4
;
