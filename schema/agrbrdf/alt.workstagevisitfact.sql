--
-- Name: obid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY workstagevisitfact ALTER COLUMN obid SET DEFAULT nextval(('ob_obidseq'::text)::regclass);


--
-- Name: obtypeid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY workstagevisitfact ALTER COLUMN obtypeid SET DEFAULT 0;


--
-- Name: createddate; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY workstagevisitfact ALTER COLUMN createddate SET DEFAULT now();


--
-- Name: checkedout; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY workstagevisitfact ALTER COLUMN checkedout SET DEFAULT false;


--
-- Name: statuscode; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY workstagevisitfact ALTER COLUMN statuscode SET DEFAULT 1;


--
-- Name: workstagevisitfact_obid_key; Type: CONSTRAINT; Schema: public; Owner: agrbrdf; Tablespace: 
--

ALTER TABLE ONLY workstagevisitfact
    ADD CONSTRAINT workstagevisitfact_obid_key UNIQUE (obid);


--
-- Name: anneoconnelprobenames_prop; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX anneoconnelprobenames_prop ON anneoconnelprobenames USING btree (propname);


--
-- Name: blastn_results_queryid; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX blastn_results_queryid ON blastn_results USING btree (queryid);


--
-- Name: blastn_results_queryidevalue; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX blastn_results_queryidevalue ON blastn_results USING btree (queryid, evalue);


--
-- Name: blastn_results_queryidevaluescore; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX blastn_results_queryidevaluescore ON blastn_results USING btree (queryid, evalue, score);


--
-- Name: blastx_results_queryid; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX blastx_results_queryid ON blastx_results USING btree (queryid);


--
-- Name: blastx_results_queryidevalue; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX blastx_results_queryidevalue ON blastx_results USING btree (queryid, evalue);


--
-- Name: geo_gene; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX geo_gene ON geosubmissiondata USING btree (gene_name);


--
-- Name: geo_id_ref; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX geo_id_ref ON geosubmissiondata USING btree (id_ref);


--
-- Name: geo_symbol; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX geo_symbol ON geosubmissiondata USING btree (genesymbol);


--
-- Name: hg18_cpg_chromstart; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX hg18_cpg_chromstart ON hg18_cpg_location USING btree (chrom, chromstart);


--
-- Name: hg18_cpg_chromstartstop; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX hg18_cpg_chromstartstop ON hg18_cpg_location USING btree (chrom, chromstart, chromend);


--
-- Name: hg18_mspi_chromstart; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX hg18_mspi_chromstart ON hg18_mspi_digest USING btree (chrom, start);


--
-- Name: hg18_mspi_chromstartstop; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX hg18_mspi_chromstartstop ON hg18_mspi_digest USING btree (chrom, start, stop);


--
-- Name: hg18_refgenes_cdsstart; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX hg18_refgenes_cdsstart ON hg18_refgenes_location USING btree (chrom, cdsstart);


--
-- Name: hg18_refgenes_cdsstartstop; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX hg18_refgenes_cdsstartstop ON hg18_refgenes_location USING btree (chrom, cdsstart, cdsend);


--
-- Name: hg18_refgenes_transstart; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX hg18_refgenes_transstart ON hg18_refgenes_location USING btree (chrom, transcriptionstart, strand);


--
-- Name: hg18_refgenes_transstartstop; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX hg18_refgenes_transstartstop ON hg18_refgenes_location USING btree (chrom, transcriptionstart, transcriptionend);


--
-- Name: hg18_refgenes_transstop; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX hg18_refgenes_transstop ON hg18_refgenes_location USING btree (chrom, transcriptionend, strand);


--
-- Name: i_analysisfunction1; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_analysisfunction1 ON analysisfunction USING btree (ob, voptypeid);


--
-- Name: i_bioprotocoloblsid; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_bioprotocoloblsid ON bioprotocolob USING btree (xreflsid);


--
-- Name: i_biosamplefact1; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_biosamplefact1 ON biosamplefact USING btree (biosampleob);


--
-- Name: i_biosamplefact2; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_biosamplefact2 ON biosamplefact USING btree (biosampleob, factnamespace, attributename);


--
-- Name: i_biosamplingfunctionlsid; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_biosamplingfunctionlsid ON biosamplingfunction USING btree (xreflsid);


--
-- Name: i_biosamplingfunctionsample; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_biosamplingfunctionsample ON biosamplingfunction USING btree (biosampleob);


--
-- Name: i_biosamplingfunctionsubject; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_biosamplingfunctionsubject ON biosamplingfunction USING btree (biosubjectob);


--
-- Name: i_biosequencefact1; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_biosequencefact1 ON biosequencefact USING btree (biosequenceob, factnamespace, attributename);


--
-- Name: i_biosequencefeatfact1; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_biosequencefeatfact1 ON biosequencefeaturefact USING btree (biosequenceob);


--
-- Name: i_biosequencefeatfactacc; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_biosequencefeatfactacc ON biosequencefeaturefact USING btree (featureaccession);


--
-- Name: i_biosequencefeaturefactlsid; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_biosequencefeaturefactlsid ON biosequencefeaturefact USING btree (xreflsid);


--
-- Name: i_biosequenceobkw; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_biosequenceobkw ON biosequenceob USING btree (obkeywords);


--
-- Name: i_biosequenceoblsid; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_biosequenceoblsid ON biosequenceob USING btree (xreflsid);


--
-- Name: i_biosequenceobsn; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_biosequenceobsn ON biosequenceob USING btree (sequencename);


--
-- Name: i_biosubjectfact1; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_biosubjectfact1 ON biosubjectfact USING btree (biosubjectob);


--
-- Name: i_biosubjectfact2; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_biosubjectfact2 ON biosubjectfact USING btree (biosubjectob, factnamespace, attributename);


--
-- Name: i_bovine_est_entropies_estname; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_bovine_est_entropies_estname ON bovine_est_entropies USING btree (estname);


--
-- Name: i_commentlink; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_commentlink ON commentlink USING btree (ob, commentob);


--
-- Name: i_commentoblsid; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_commentoblsid ON commentob USING btree (xreflsid);


--
-- Name: i_datasourcefact; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_datasourcefact ON datasourcefact USING btree (datasourceob, factnamespace, attributename);


--
-- Name: i_datasourcename; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_datasourcename ON datasourceob USING btree (datasourcename);


--
-- Name: i_datasourceoblsid; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_datasourceoblsid ON datasourceob USING btree (xreflsid);


--
-- Name: i_dbsearchobservation_hit; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_dbsearchobservation_hit ON databasesearchobservation USING btree (hitsequence);


--
-- Name: i_dbsearchobservation_lsid; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_dbsearchobservation_lsid ON databasesearchobservation USING btree (xreflsid);


--
-- Name: i_dbsearchobservation_query; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_dbsearchobservation_query ON databasesearchobservation USING btree (querysequence);


--
-- Name: i_dbsearchobservation_queryhit; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_dbsearchobservation_queryhit ON databasesearchobservation USING btree (querysequence, hitsequence);


--
-- Name: i_dbsearchobservation_studyhit; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_dbsearchobservation_studyhit ON databasesearchobservation USING btree (databasesearchstudy, hitsequence);


--
-- Name: i_dbsearchobservation_studyquery; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_dbsearchobservation_studyquery ON databasesearchobservation USING btree (databasesearchstudy, querysequence);


--
-- Name: i_dbsearchobservation_studyqueryhit; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_dbsearchobservation_studyqueryhit ON databasesearchobservation USING btree (databasesearchstudy, querysequence, hitsequence);


--
-- Name: i_displayfunctionds; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_displayfunctionds ON displayfunction USING btree (datasourceob);


--
-- Name: i_displayfunctionlsid; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_displayfunctionlsid ON displayfunction USING btree (xreflsid);


--
-- Name: i_displayfunctionob; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_displayfunctionob ON displayfunction USING btree (ob);


--
-- Name: i_displayfunctionobdp; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_displayfunctionobdp ON displayfunction USING btree (ob, displayprocedureob);


--
-- Name: i_displayprocedureoblsid; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_displayprocedureoblsid ON displayprocedureob USING btree (xreflsid);


--
-- Name: i_gbs_yield_import_temp_rss; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_gbs_yield_import_temp_rss ON gbs_yield_import_temp USING btree (run, sqname, sampleid);


--
-- Name: i_gbs_yield_import_temp_run; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_gbs_yield_import_temp_run ON gbs_yield_import_temp USING btree (run);


--
-- Name: i_gbs_yield_import_temp_samp; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_gbs_yield_import_temp_samp ON gbs_yield_import_temp USING btree (sampleid);


--
-- Name: i_gbs_yield_import_temp_sq; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_gbs_yield_import_temp_sq ON gbs_yield_import_temp USING btree (sqname);


--
-- Name: i_gbskeyfilefact_biosubject; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_gbskeyfilefact_biosubject ON gbskeyfilefact USING btree (biosubjectob);


--
-- Name: i_gbskeyfilefactsfl; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_gbskeyfilefactsfl ON gbskeyfilefact USING btree (sample, flowcell, lane);


--
-- Name: i_gbsyieldfactsamp; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_gbsyieldfactsamp ON gbsyieldfact USING btree (sampleid);


--
-- Name: i_gbsyieldfactsfl; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_gbsyieldfactsfl ON gbsyieldfact USING btree (sampleid, flowcell, lane);


--
-- Name: i_gbsyieldfactsq; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_gbsyieldfactsq ON gbsyieldfact USING btree (sqname);


--
-- Name: i_gbsyieldfactsqsamp; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_gbsyieldfactsqsamp ON gbsyieldfact USING btree (sqname, sampleid);


--
-- Name: i_gene2accession_geneid; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_gene2accession_geneid ON gene2accession USING btree (geneid);


--
-- Name: i_gene2accession_genomic; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_gene2accession_genomic ON gene2accession USING btree (genomic_nucleotide_accession);


--
-- Name: i_gene2accession_nuc; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_gene2accession_nuc ON gene2accession USING btree (rna_nucleotide_accession);


--
-- Name: i_gene2accession_prot; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_gene2accession_prot ON gene2accession USING btree (protein_accession);


--
-- Name: i_gene2accession_taxid; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_gene2accession_taxid ON gene2accession USING btree (tax_id);


--
-- Name: i_geneexpressionstudylsid; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_geneexpressionstudylsid ON geneexpressionstudy USING btree (xreflsid);


--
-- Name: i_geneexpressionstudyname; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_geneexpressionstudyname ON geneexpressionstudy USING btree (studyname);


--
-- Name: i_geneproductlinkgene; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_geneproductlinkgene ON geneproductlink USING btree (geneticob);


--
-- Name: i_geneproductlinklsid; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_geneproductlinklsid ON geneproductlink USING btree (xreflsid);


--
-- Name: i_geneproductlinkprod; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_geneproductlinkprod ON geneproductlink USING btree (biosequenceob);


--
-- Name: i_generegulationlinklsid; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_generegulationlinklsid ON generegulationlink USING btree (xreflsid);


--
-- Name: i_geneticexpress_bioseq; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_geneticexpress_bioseq ON geneticexpressionfact USING btree (biosequenceob);


--
-- Name: i_geneticexpress_bioseqv; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_geneticexpress_bioseqv ON geneticexpressionfact USING btree (biosequenceob, voptypeid);


--
-- Name: i_geneticexpress_gene; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_geneticexpress_gene ON geneticexpressionfact USING btree (geneticob);


--
-- Name: i_geneticexpressionfactlsid; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_geneticexpressionfactlsid ON geneticexpressionfact USING btree (xreflsid);


--
-- Name: i_geneticfactlsid; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_geneticfactlsid ON geneticfact USING btree (xreflsid);


--
-- Name: i_geneticfunctionfactlsid; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_geneticfunctionfactlsid ON geneticfunctionfact USING btree (xreflsid);


--
-- Name: i_geneticlocationfactgeneid; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_geneticlocationfactgeneid ON geneticlocationfact USING btree (entrezgeneid);


--
-- Name: i_geneticlocationfactgeneticob; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_geneticlocationfactgeneticob ON geneticlocationfact USING btree (geneticob);


--
-- Name: i_geneticlocationfactlsid; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_geneticlocationfactlsid ON geneticlocationfact USING btree (xreflsid);


--
-- Name: i_geneticlocationfactmulti1; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_geneticlocationfactmulti1 ON geneticlocationfact USING btree (entrezgeneid, evidence, geneticob);


--
-- Name: i_geneticlocationfactmulti2; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_geneticlocationfactmulti2 ON geneticlocationfact USING btree (mapname, chromosomename, locationstart);


--
-- Name: i_geneticlocationfactmulti3; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_geneticlocationfactmulti3 ON geneticlocationfact USING btree (biosequenceob, mapname, chromosomename);


--
-- Name: i_geneticlocationfactmulti4; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_geneticlocationfactmulti4 ON geneticlocationfact USING btree (biosequenceob, mapname);


--
-- Name: i_geneticlocationfactseqid; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_geneticlocationfactseqid ON geneticlocationfact USING btree (biosequenceob);


--
-- Name: i_geneticlocationlistlsid; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_geneticlocationlistlsid ON geneticlocationlist USING btree (xreflsid);


--
-- Name: i_geneticoblistlsid; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_geneticoblistlsid ON geneticoblist USING btree (xreflsid);


--
-- Name: i_geneticoblsid; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_geneticoblsid ON geneticob USING btree (xreflsid);


--
-- Name: i_geneticobsymbols; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_geneticobsymbols ON geneticob USING btree (geneticobsymbols);


--
-- Name: i_genetictestfact2all; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_genetictestfact2all ON genetictestfact2 USING btree (genetictestfact, factnamespace, attributename);


--
-- Name: i_genetictestfactlsid; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_genetictestfactlsid ON genetictestfact USING btree (xreflsid);


--
-- Name: i_genotpyestudysample1; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_genotpyestudysample1 ON genotypestudy USING btree (biosampleob);


--
-- Name: i_genotypeobservationfact1; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_genotypeobservationfact1 ON genotypeobservationfact USING btree (genotypeobservation);


--
-- Name: i_genotypeobservationlsid; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_genotypeobservationlsid ON genotypeobservation USING btree (xreflsid);


--
-- Name: i_genotypeobservationstudy1; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_genotypeobservationstudy1 ON genotypeobservation USING btree (genotypestudy);


--
-- Name: i_genotypeobservationtest1; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_genotypeobservationtest1 ON genotypeobservation USING btree (genetictestfact);


--
-- Name: i_genotypestudylsid; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_genotypestudylsid ON genotypestudy USING btree (xreflsid);


--
-- Name: i_geo_poolid1; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_geo_poolid1 ON geosubmissiondata USING btree (poolid1);


--
-- Name: i_gpl3802_probe_set_id; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_gpl3802_probe_set_id ON gpl3802_annotation USING btree (probe_set_id);


--
-- Name: i_harvestwheatchip_annotation_ap; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_harvestwheatchip_annotation_ap ON harvestwheatchip_annotation USING btree (all_probes);


--
-- Name: i_importfunctionlsid; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_importfunctionlsid ON importfunction USING btree (xreflsid);


--
-- Name: i_importprocedureoblsid; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_importprocedureoblsid ON importprocedureob USING btree (xreflsid);


--
-- Name: i_labresourcelistlsid; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_labresourcelistlsid ON labresourcelist USING btree (xreflsid);


--
-- Name: i_labresourceoblsid; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_labresourceoblsid ON labresourceob USING btree (xreflsid);


--
-- Name: i_lisafanseriesnormalisation_0; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_lisafanseriesnormalisation_0 ON lisafanseriesnormalisation USING btree (datasourceob, voptypeid);


--
-- Name: i_listmembershipfact1; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_listmembershipfact1 ON listmembershipfact USING btree (memberid);


--
-- Name: i_listmembershipfact2; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_listmembershipfact2 ON listmembershipfact USING btree (oblist, memberid);


--
-- Name: i_listmembershiplink_list; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_listmembershiplink_list ON listmembershiplink USING btree (oblist);


--
-- Name: i_listmembershipob; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_listmembershipob ON listmembershiplink USING btree (ob);


--
-- Name: i_literaturereferenceoblsid; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_literaturereferenceoblsid ON literaturereferenceob USING btree (xreflsid);


--
-- Name: i_microarrayfactlsid; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_microarrayfactlsid ON microarrayfact USING btree (xreflsid);


--
-- Name: i_microarrayobservationfactobs; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_microarrayobservationfactobs ON microarrayobservationfact USING btree (microarrayobservation);


--
-- Name: i_microarrayobslsid; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_microarrayobslsid ON microarrayobservation USING btree (xreflsid);


--
-- Name: i_microarrayspotfact_lrgal; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_microarrayspotfact_lrgal ON microarrayspotfact USING btree (labresourceob, gal_name);


--
-- Name: i_microarrayspotfactaccession; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_microarrayspotfactaccession ON microarrayspotfact USING btree (accession);


--
-- Name: i_microarrayspotfactgalid; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_microarrayspotfactgalid ON microarrayspotfact USING btree (gal_id);


--
-- Name: i_microarrayspotfactgene; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_microarrayspotfactgene ON microarrayspotfact USING btree (gal_genename);


--
-- Name: i_microarrayspotfactloc1; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_microarrayspotfactloc1 ON microarrayspotfact USING btree (labresourceob, gal_block, gal_column, gal_row);


--
-- Name: i_microarrayspotfactlsid; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_microarrayspotfactlsid ON microarrayspotfact USING btree (xreflsid);


--
-- Name: i_oblistlsid; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_oblistlsid ON oblist USING btree (xreflsid);


--
-- Name: i_obxreflsid1; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_obxreflsid1 ON ob USING btree (xreflsid);


--
-- Name: i_ontologyobname; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_ontologyobname ON ontologyob USING btree (ontologyname);


--
-- Name: i_ontologyobxreflsid; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_ontologyobxreflsid ON ontologyob USING btree (xreflsid);


--
-- Name: i_ontologytermfact2all; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_ontologytermfact2all ON ontologytermfact2 USING btree (factnamespace, attributename, attributevalue);


--
-- Name: i_ontologytermfact2av; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_ontologytermfact2av ON ontologytermfact2 USING btree (attributevalue);


--
-- Name: i_ontologytermfact2tav; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_ontologytermfact2tav ON ontologytermfact2 USING btree (ontologytermid, factnamespace, attributevalue);


--
-- Name: i_ontologytermfactlsid; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_ontologytermfactlsid ON ontologytermfact USING btree (xreflsid);


--
-- Name: i_ontologytermfacto; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_ontologytermfacto ON ontologytermfact USING btree (ontologyob);


--
-- Name: i_ontologytermfactterm; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_ontologytermfactterm ON ontologytermfact USING btree (termname);


--
-- Name: i_oplsid; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_oplsid ON op USING btree (xreflsid);


--
-- Name: i_phenotypeobservationlsid; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_phenotypeobservationlsid ON phenotypeobservation USING btree (xreflsid);


--
-- Name: i_phenotypestudylsid; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_phenotypestudylsid ON phenotypestudy USING btree (xreflsid);


--
-- Name: i_predicatelink1; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_predicatelink1 ON predicatelink USING btree (objectob, subjectob, predicate);


--
-- Name: i_predicatelink2; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_predicatelink2 ON predicatelink USING btree (subjectob, predicate);


--
-- Name: i_predicatelink3; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_predicatelink3 ON predicatelink USING btree (objectob, predicate);


--
-- Name: i_predicatelinklsid; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_predicatelinklsid ON predicatelink USING btree (xreflsid);


--
-- Name: i_securityfunction_ob; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_securityfunction_ob ON securityfunction USING btree (ob);


--
-- Name: i_securityfunction_type; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_securityfunction_type ON securityfunction USING btree (applytotype);


--
-- Name: i_sequencealignmentfact_lsid; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_sequencealignmentfact_lsid ON sequencealignmentfact USING btree (xreflsid);


--
-- Name: i_sequencealignmentfact_ob; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_sequencealignmentfact_ob ON sequencealignmentfact USING btree (databasesearchobservation);


--
-- Name: i_sequencingfunctionlsid; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_sequencingfunctionlsid ON sequencingfunction USING btree (xreflsid);


--
-- Name: i_sequencingfunctionsample; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_sequencingfunctionsample ON sequencingfunction USING btree (biosampleob);


--
-- Name: i_sequencingfunctionseq; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_sequencingfunctionseq ON sequencingfunction USING btree (biosequenceob);


--
-- Name: i_staffoblsid; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_staffoblsid ON staffob USING btree (xreflsid);


--
-- Name: i_tanimalfact_animalid; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_tanimalfact_animalid ON t_animal_fact USING btree (animalid);


--
-- Name: i_tanimalfact_ob; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_tanimalfact_ob ON t_animal_fact USING btree (biosubjectob);


--
-- Name: i_tsamplefact_animalid; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_tsamplefact_animalid ON t_sample_fact USING btree (animalid);


--
-- Name: i_tsamplefact_ob; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_tsamplefact_ob ON t_sample_fact USING btree (biosubjectob);


--
-- Name: i_tsamplefact_sampleid; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_tsamplefact_sampleid ON t_sample_fact USING btree (sampleid);


--
-- Name: i_uri_temp; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_uri_temp ON uriob USING btree (uristring);


--
-- Name: i_urilinkob; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_urilinkob ON urilink USING btree (ob);


--
-- Name: i_urilinkoburiob; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_urilinkoburiob ON urilink USING btree (uriob, ob);


--
-- Name: i_urilinkuriob; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_urilinkuriob ON urilink USING btree (uriob);


--
-- Name: i_urilsid; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_urilsid ON uriob USING btree (xreflsid);


--
-- Name: i_wheatchipannotation2011_probeset; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_wheatchipannotation2011_probeset ON wheatchipannotation2011 USING btree (probeset);


--
-- Name: i_workflowlinklsid; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_workflowlinklsid ON workflowlink USING btree (xreflsid);


--
-- Name: i_workflowmembershiplinklsid; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_workflowmembershiplinklsid ON workflowmembershiplink USING btree (xreflsid);


--
-- Name: i_workflowoblsid; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_workflowoblsid ON workflowob USING btree (xreflsid);


--
-- Name: i_workflowstageoblsid; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_workflowstageoblsid ON workflowstageob USING btree (xreflsid);


--
-- Name: i_workstagevisitfactlsid; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX i_workstagevisitfactlsid ON workstagevisitfact USING btree (xreflsid);


--
-- Name: ianneoconnelarrays2_p; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX ianneoconnelarrays2_p ON anneoconnelarrays2 USING btree (dbprobes);


--
-- Name: ibt4wgsnppanel_v6_3cmarkernames1; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX ibt4wgsnppanel_v6_3cmarkernames1 ON bt4wgsnppanel_v6_3cmarkernames USING btree (name);


--
-- Name: ibt4wgsnppanel_v6_3cmarkernames2; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX ibt4wgsnppanel_v6_3cmarkernames2 ON bt4wgsnppanel_v6_3cmarkernames USING btree (onchipname);


--
-- Name: ics34clusterpaperdata_contig; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX ics34clusterpaperdata_contig ON cs34clusterpaperdata USING btree (contigname);


--
-- Name: ifilerecgeosubmission; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX ifilerecgeosubmission ON geosubmissiondata USING btree (filerecnum);


--
-- Name: igene_infogeneid; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX igene_infogeneid ON gene_info USING btree (geneid);


--
-- Name: igene_infosymtax; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX igene_infosymtax ON gene_info USING btree (symbol, tax_id);


--
-- Name: igenotypes; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX igenotypes ON genotypes USING btree (snp_name);


--
-- Name: igpl7083_34008annotationensid; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX igpl7083_34008annotationensid ON gpl7083_34008annotation USING btree (ensembl_id);


--
-- Name: igpl7083_34008annotationgbacc; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX igpl7083_34008annotationgbacc ON gpl7083_34008annotation USING btree (gb_acc);


--
-- Name: ihg18uniquereads_hit; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX ihg18uniquereads_hit ON hg18uniquereads USING btree (mappedtofrag);


--
-- Name: ihg18uniquereads_query; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX ihg18uniquereads_query ON hg18uniquereads USING btree (queryfrag);


--
-- Name: iimportfunction_ds; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX iimportfunction_ds ON importfunction USING btree (datasourceob);


--
-- Name: iimportfunction_ob; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX iimportfunction_ob ON importfunction USING btree (ob);


--
-- Name: ijunk; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX ijunk ON junk USING btree (obid);


--
-- Name: ijunk1; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX ijunk1 ON junk1 USING btree (datasourcelsid);


--
-- Name: ilicnormalisation1_probeset; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX ilicnormalisation1_probeset ON licnormalisation1 USING btree (probeset);


--
-- Name: imicroarrayobservation_ms; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX imicroarrayobservation_ms ON microarrayobservation USING btree (microarraystudy);


--
-- Name: imicroarrayobservation_msf; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX imicroarrayobservation_msf ON microarrayobservation USING btree (microarrayspotfact);


--
-- Name: imicroarrayobservation_msfs; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX imicroarrayobservation_msfs ON microarrayobservation USING btree (microarraystudy, microarrayspotfact);


--
-- Name: iprint139annotation_en; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX iprint139annotation_en ON print139annotation_v1 USING btree (estname);


--
-- Name: iprint139annotation_gn; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX iprint139annotation_gn ON print139annotation_v1 USING btree (arraygene_name);


--
-- Name: iprint139annotationv1_c; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX iprint139annotationv1_c ON print139annotation_v1 USING btree (contentid);


--
-- Name: ireproductionmicroarrayplasmids_mc; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX ireproductionmicroarrayplasmids_mc ON reproductionmicroarrayplasmids USING btree (microarray_code);


--
-- Name: iseqname; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX iseqname ON sheepv3_prot_annotation USING btree (seqname);


--
-- Name: ispotidmapcaco2; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX ispotidmapcaco2 ON spotidmapcaco2 USING btree (recnum);


--
-- Name: istart_hg18_cpg_mspi_overlap; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX istart_hg18_cpg_mspi_overlap ON hg18_cpg_mspi_overlap USING btree (chrom, start);


--
-- Name: istop_hg18_cpg_mspi_overlap; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX istop_hg18_cpg_mspi_overlap ON hg18_cpg_mspi_overlap USING btree (chrom, stop);


--
-- Name: isystem_blastn_results; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX isystem_blastn_results ON blastn_results USING btree (datasourceob, voptypeid);


--
-- Name: isystem_geosubmissiondata; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX isystem_geosubmissiondata ON geosubmissiondata USING btree (datasourceob, voptypeid);


--
-- Name: isystem_gpl3802_annotation; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX isystem_gpl3802_annotation ON gpl3802_annotation USING btree (datasourceob, voptypeid);


--
-- Name: isystem_harvestwheatchip_annotation; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX isystem_harvestwheatchip_annotation ON harvestwheatchip_annotation USING btree (datasourceob, voptypeid);


--
-- Name: isystem_sheepv3_prot_annotation; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX isystem_sheepv3_prot_annotation ON sheepv3_prot_annotation USING btree (datasourceob, voptypeid);


--
-- Name: isystem_spotidmapcaco2; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX isystem_spotidmapcaco2 ON spotidmapcaco2 USING btree (datasourceob, voptypeid);


--
-- Name: isystem_wheatchipannotation2011; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX isystem_wheatchipannotation2011 ON wheatchipannotation2011 USING btree (datasourceob, voptypeid);


--
-- Name: isystem_wheatrma; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX isystem_wheatrma ON wheatrma USING btree (datasourceob, voptypeid);


--
-- Name: isystemanneoconnelarrays2; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX isystemanneoconnelarrays2 ON anneoconnelarrays2 USING btree (datasourceob, voptypeid);


--
-- Name: isystemanneoconnelprobenames; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX isystemanneoconnelprobenames ON anneoconnelprobenames USING btree (datasourceob, voptypeid);


--
-- Name: isystembt4wgsnppanel_v6_3cmarkernames; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX isystembt4wgsnppanel_v6_3cmarkernames ON bt4wgsnppanel_v6_3cmarkernames USING btree (datasourceob, voptypeid);


--
-- Name: isystemcpgfragmentsneargenes; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX isystemcpgfragmentsneargenes ON cpgfragmentsneargenes USING btree (datasourceob, voptypeid);


--
-- Name: isystemcs34clusterpaperdata; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX isystemcs34clusterpaperdata ON cs34clusterpaperdata USING btree (datasourceob, voptypeid);


--
-- Name: isystemdata_set_1_genstat_results_180908; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX isystemdata_set_1_genstat_results_180908 ON data_set_1_genstat_results_180908 USING btree (datasourceob, voptypeid);


--
-- Name: isystemdata_set_2_r_results_180908; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX isystemdata_set_2_r_results_180908 ON data_set_2_r_results_180908 USING btree (datasourceob, voptypeid);


--
-- Name: isystemgene2accession; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX isystemgene2accession ON gene2accession USING btree (datasourceob, voptypeid);


--
-- Name: isystemgene_info; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX isystemgene_info ON gene_info USING btree (datasourceob, voptypeid);


--
-- Name: isystemgenotypes; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX isystemgenotypes ON genotypes USING btree (datasourceob, voptypeid);


--
-- Name: isystemgpl7083_34008annotation; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX isystemgpl7083_34008annotation ON gpl7083_34008annotation USING btree (datasourceob, voptypeid);


--
-- Name: isystemhg18_cpg_location; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX isystemhg18_cpg_location ON hg18_cpg_location USING btree (datasourceob, voptypeid);


--
-- Name: isystemhg18_cpg_mspi_overlap; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX isystemhg18_cpg_mspi_overlap ON hg18_cpg_mspi_overlap USING btree (datasourceob, voptypeid);


--
-- Name: isystemhg18_mspi_digest; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX isystemhg18_mspi_digest ON hg18_mspi_digest USING btree (datasourceob, voptypeid);


--
-- Name: isystemhg18_refgenes_location; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX isystemhg18_refgenes_location ON hg18_refgenes_location USING btree (datasourceob, voptypeid);


--
-- Name: isystemhg18uniquereads; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX isystemhg18uniquereads ON hg18uniquereads USING btree (datasourceob, voptypeid);


--
-- Name: isystemlicexpression1; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX isystemlicexpression1 ON licexpression1 USING btree (datasourceob, voptypeid);


--
-- Name: isystemlicnormalisation1; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX isystemlicnormalisation1 ON licnormalisation1 USING btree (datasourceob, voptypeid);


--
-- Name: isystemlisafanseriesnormalisation; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX isystemlisafanseriesnormalisation ON lisafanseriesnormalisation USING btree (datasourceob, voptypeid);


--
-- Name: isystemoracle_microarray_experiment; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX isystemoracle_microarray_experiment ON oracle_microarray_experiment USING btree (datasourceob, voptypeid);


--
-- Name: isystemprint139annotation; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX isystemprint139annotation ON print139annotation USING btree (datasourceob, voptypeid);


--
-- Name: isystemprint139annotation_v1; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX isystemprint139annotation_v1 ON print139annotation_v1 USING btree (datasourceob, voptypeid);


--
-- Name: isystemreproductionmicroarrayplasmids; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX isystemreproductionmicroarrayplasmids ON reproductionmicroarrayplasmids USING btree (datasourceob, voptypeid);


--
-- Name: isystemtaxonomy_names; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX isystemtaxonomy_names ON taxonomy_names USING btree (datasourceob, voptypeid);


--
-- Name: itax_id; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX itax_id ON taxonomy_names USING btree (tax_id);


--
-- Name: licexpression1gene; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX licexpression1gene ON licexpression1 USING btree (affygene);


--
-- Name: lisafan_expt136_lowscan_no_bg_corr_gene; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX lisafan_expt136_lowscan_no_bg_corr_gene ON lisafan_expt136_lowscan_no_bg_corr_delete01102008 USING btree (gene_name);


--
-- Name: lisafanseriesnormalisationgene; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX lisafanseriesnormalisationgene ON lisafanseriesnormalisation USING btree (gene_name);


--
-- Name: print139annotationcontent; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX print139annotationcontent ON print139annotation USING btree (contentid);


--
-- Name: print139annotationestname; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX print139annotationestname ON print139annotation USING btree (estname);


--
-- Name: systemgeosubmissiondata; Type: INDEX; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE INDEX systemgeosubmissiondata ON geosubmissiondata USING btree (datasourceob, voptypeid);


--
-- Name: checkaccesslinkkey; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER checkaccesslinkkey
    BEFORE INSERT OR UPDATE ON accesslink
    FOR EACH ROW
    EXECUTE PROCEDURE checkaccesslinkkey();


--
-- Name: checkaccessontology; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER checkaccessontology
    BEFORE INSERT OR UPDATE ON accesslink
    FOR EACH ROW
    EXECUTE PROCEDURE checkaccessontology();


--
-- Name: checkaccessontology; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER checkaccessontology
    BEFORE INSERT OR UPDATE ON accessfact
    FOR EACH ROW
    EXECUTE PROCEDURE checkaccessontology();


--
-- Name: checkaliquotrecord; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER checkaliquotrecord
    BEFORE INSERT OR UPDATE ON biosamplealiquotfact
    FOR EACH ROW
    EXECUTE PROCEDURE checkaliquotrecord();


--
-- Name: checkanalysisfunctionobkey; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER checkanalysisfunctionobkey
    BEFORE INSERT OR UPDATE ON analysisfunction
    FOR EACH ROW
    EXECUTE PROCEDURE checkanalysisfunctionobkey();


--
-- Name: checkanalysistypeontology; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER checkanalysistypeontology
    BEFORE INSERT OR UPDATE ON analysisprocedureob
    FOR EACH ROW
    EXECUTE PROCEDURE checkanalysistypeontology();


--
-- Name: checkbiodatabasetypeontology; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER checkbiodatabasetypeontology
    BEFORE INSERT OR UPDATE ON biodatabaseob
    FOR EACH ROW
    EXECUTE PROCEDURE checkbiodatabasetype();


--
-- Name: checkbiolibrarytypeontology; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER checkbiolibrarytypeontology
    BEFORE INSERT OR UPDATE ON biolibraryob
    FOR EACH ROW
    EXECUTE PROCEDURE checkbiolibrarytypeontology();


--
-- Name: checkbioprotocoltypeontology; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER checkbioprotocoltypeontology
    BEFORE INSERT OR UPDATE ON bioprotocolob
    FOR EACH ROW
    EXECUTE PROCEDURE checkbioprotocoltypeontology();


--
-- Name: checkbiosampletypeontology; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER checkbiosampletypeontology
    BEFORE INSERT OR UPDATE ON biosampleob
    FOR EACH ROW
    EXECUTE PROCEDURE checkbiosampletypeontology();


--
-- Name: checkcommentedobkey; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER checkcommentedobkey
    BEFORE INSERT OR UPDATE ON commentob
    FOR EACH ROW
    EXECUTE PROCEDURE checkcommentedobkey();


--
-- Name: checkcommentlinkkey; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER checkcommentlinkkey
    BEFORE INSERT OR UPDATE ON commentlink
    FOR EACH ROW
    EXECUTE PROCEDURE checkcommentlinkkey();


--
-- Name: checkdatabasesearchstudytypeontology; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER checkdatabasesearchstudytypeontology
    BEFORE INSERT OR UPDATE ON databasesearchstudy
    FOR EACH ROW
    EXECUTE PROCEDURE checkdatabasesearchstudytypeontology();


--
-- Name: checkdatasourceontology; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER checkdatasourceontology
    BEFORE INSERT OR UPDATE ON datasourceob
    FOR EACH ROW
    EXECUTE PROCEDURE checkdatasourceontology();


--
-- Name: checkdfvoptypeid; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER checkdfvoptypeid
    BEFORE INSERT OR UPDATE ON displayfunction
    FOR EACH ROW
    EXECUTE PROCEDURE checkvoptypeid();


--
-- Name: checkdisplayfunctionobkey; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER checkdisplayfunctionobkey
    BEFORE INSERT OR UPDATE ON displayfunction
    FOR EACH ROW
    EXECUTE PROCEDURE checkdisplayfunctionobkey();


--
-- Name: checkenotypestudytypeontology; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER checkenotypestudytypeontology
    BEFORE INSERT OR UPDATE ON genotypestudy
    FOR EACH ROW
    EXECUTE PROCEDURE checkgenotypestudytypeontology();


--
-- Name: checkfeatureattributeontology; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER checkfeatureattributeontology
    BEFORE INSERT OR UPDATE ON biosequencefeatureattributefact
    FOR EACH ROW
    EXECUTE PROCEDURE checkfeatureattributeontology();


--
-- Name: checkfeatureontology; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER checkfeatureontology
    BEFORE INSERT OR UPDATE ON biosequencefeaturefact
    FOR EACH ROW
    EXECUTE PROCEDURE checkfeatureontology();


--
-- Name: checkgeneexpressionstudytypeontology; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER checkgeneexpressionstudytypeontology
    BEFORE INSERT OR UPDATE ON geneexpressionstudy
    FOR EACH ROW
    EXECUTE PROCEDURE checkgeneexpressionstudytypeontology();


--
-- Name: checkgeneticlistontology; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER checkgeneticlistontology
    BEFORE INSERT OR UPDATE ON geneticoblist
    FOR EACH ROW
    EXECUTE PROCEDURE checkgeneticlistontology();


--
-- Name: checkgeneticobontology; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER checkgeneticobontology
    BEFORE INSERT OR UPDATE ON geneticob
    FOR EACH ROW
    EXECUTE PROCEDURE checkgeneticobontology();


--
-- Name: checkgenetictestontology; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER checkgenetictestontology
    BEFORE INSERT OR UPDATE ON genetictestfact
    FOR EACH ROW
    EXECUTE PROCEDURE checkgenetictestontology();


--
-- Name: checkimportobkey; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER checkimportobkey
    BEFORE INSERT OR UPDATE ON importfunction
    FOR EACH ROW
    EXECUTE PROCEDURE checkimportobkey();


--
-- Name: checklfvoptypeid; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER checklfvoptypeid
    BEFORE INSERT OR UPDATE ON listmembershipfact
    FOR EACH ROW
    EXECUTE PROCEDURE checkvoptypeid();


--
-- Name: checkliteraturereferencelinkkey; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER checkliteraturereferencelinkkey
    BEFORE INSERT OR UPDATE ON literaturereferencelink
    FOR EACH ROW
    EXECUTE PROCEDURE checkliteraturereferencelinkkey();


--
-- Name: checklmvoptypeid; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER checklmvoptypeid
    BEFORE INSERT OR UPDATE ON listmembershiplink
    FOR EACH ROW
    EXECUTE PROCEDURE checkvoptypeid();


--
-- Name: checkoblistkey; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER checkoblistkey
    BEFORE INSERT OR UPDATE ON listmembershiplink
    FOR EACH ROW
    EXECUTE PROCEDURE checkoblistkey();


--
-- Name: checkontology; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER checkontology
    BEFORE INSERT OR UPDATE ON predicatelink
    FOR EACH ROW
    EXECUTE PROCEDURE checkpredicateontology();


--
-- Name: checkontology; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER checkontology
    BEFORE INSERT OR UPDATE ON oblist
    FOR EACH ROW
    EXECUTE PROCEDURE checklistontology();


--
-- Name: checkontologyunitname; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER checkontologyunitname
    BEFORE INSERT OR UPDATE ON ontologytermfact
    FOR EACH ROW
    EXECUTE PROCEDURE checkunitname();


--
-- Name: checkpedigreeontology; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER checkpedigreeontology
    BEFORE INSERT OR UPDATE ON pedigreelink
    FOR EACH ROW
    EXECUTE PROCEDURE checkpedigreeontology();


--
-- Name: checkphenotypeontology; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER checkphenotypeontology
    BEFORE INSERT OR UPDATE ON phenotypeobservation
    FOR EACH ROW
    EXECUTE PROCEDURE checkphenotypeontology();


--
-- Name: checkphenotypeontologyname; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER checkphenotypeontologyname
    BEFORE INSERT OR UPDATE ON phenotypestudy
    FOR EACH ROW
    EXECUTE PROCEDURE checkphenotypeontologyname();


--
-- Name: checkpredicatekeys; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER checkpredicatekeys
    BEFORE INSERT OR UPDATE ON predicatelink
    FOR EACH ROW
    EXECUTE PROCEDURE checkpredicatekeys();


--
-- Name: checksampleunits; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER checksampleunits
    BEFORE INSERT OR UPDATE ON biosampleob
    FOR EACH ROW
    EXECUTE PROCEDURE checksampleunits();


--
-- Name: checksamplingunitname; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER checksamplingunitname
    BEFORE INSERT OR UPDATE ON biosamplingfact
    FOR EACH ROW
    EXECUTE PROCEDURE checkunitname();


--
-- Name: checksecurityfunctionobkey; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER checksecurityfunctionobkey
    BEFORE INSERT OR UPDATE ON securityfunction
    FOR EACH ROW
    EXECUTE PROCEDURE checksecurityfunctionobkey();


--
-- Name: checksequenceontology; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER checksequenceontology
    BEFORE INSERT OR UPDATE ON biosequenceob
    FOR EACH ROW
    EXECUTE PROCEDURE checksequenceontology();


--
-- Name: checksfvoptypeid; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER checksfvoptypeid
    BEFORE INSERT OR UPDATE ON sequencingfunction
    FOR EACH ROW
    EXECUTE PROCEDURE checkvoptypeid();


--
-- Name: checkurilinkkey; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER checkurilinkkey
    BEFORE INSERT OR UPDATE ON urilink
    FOR EACH ROW
    EXECUTE PROCEDURE checkurilinkkey();


--
-- Name: checkworkflowontology; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER checkworkflowontology
    BEFORE INSERT OR UPDATE ON workflowstageob
    FOR EACH ROW
    EXECUTE PROCEDURE checkworkflowontology();


--
-- Name: filterkeywords; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER filterkeywords
    BEFORE INSERT OR UPDATE ON ob
    FOR EACH ROW
    EXECUTE PROCEDURE filterkeywords('obkeywords');


--
-- Name: filterkeywords; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER filterkeywords
    BEFORE INSERT OR UPDATE ON biosubjectob
    FOR EACH ROW
    EXECUTE PROCEDURE filterkeywords('obkeywords');


--
-- Name: filterkeywords; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER filterkeywords
    BEFORE INSERT OR UPDATE ON microarrayspotfact
    FOR EACH ROW
    EXECUTE PROCEDURE filterkeywords('obkeywords');


--
-- Name: labresourcetypecheck; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER labresourcetypecheck
    BEFORE INSERT OR UPDATE ON labresourceob
    FOR EACH ROW
    EXECUTE PROCEDURE checklabresourceontology();


--
-- Name: setobtype; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER setobtype
    BEFORE INSERT ON ontologyob
    FOR EACH ROW
    EXECUTE PROCEDURE setobtype('5');


--
-- Name: setobtype; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER setobtype
    BEFORE INSERT ON ontologytermfact
    FOR EACH ROW
    EXECUTE PROCEDURE setobtype('10');


--
-- Name: setobtype; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER setobtype
    BEFORE INSERT ON predicatelink
    FOR EACH ROW
    EXECUTE PROCEDURE setobtype('15');


--
-- Name: setobtype; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER setobtype
    BEFORE INSERT ON oblist
    FOR EACH ROW
    EXECUTE PROCEDURE setobtype('20');


--
-- Name: setobtype; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER setobtype
    BEFORE INSERT ON uriob
    FOR EACH ROW
    EXECUTE PROCEDURE setobtype('30');


--
-- Name: setobtype; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER setobtype
    BEFORE INSERT ON commentob
    FOR EACH ROW
    EXECUTE PROCEDURE setobtype('40');


--
-- Name: setobtype; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER setobtype
    BEFORE INSERT ON staffob
    FOR EACH ROW
    EXECUTE PROCEDURE setobtype('50');


--
-- Name: setobtype; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER setobtype
    BEFORE INSERT ON literaturereferenceob
    FOR EACH ROW
    EXECUTE PROCEDURE setobtype('60');


--
-- Name: setobtype; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER setobtype
    BEFORE INSERT ON labresourceob
    FOR EACH ROW
    EXECUTE PROCEDURE setobtype('70');


--
-- Name: setobtype; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER setobtype
    BEFORE INSERT ON labresourcelist
    FOR EACH ROW
    EXECUTE PROCEDURE setobtype('75');


--
-- Name: setobtype; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER setobtype
    BEFORE INSERT ON biosubjectob
    FOR EACH ROW
    EXECUTE PROCEDURE setobtype('85');


--
-- Name: setobtype; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER setobtype
    BEFORE INSERT ON biosampleob
    FOR EACH ROW
    EXECUTE PROCEDURE setobtype('90');


--
-- Name: setobtype; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER setobtype
    BEFORE INSERT ON bioprotocolob
    FOR EACH ROW
    EXECUTE PROCEDURE setobtype('95');


--
-- Name: setobtype; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER setobtype
    BEFORE INSERT ON biosamplingfunction
    FOR EACH ROW
    EXECUTE PROCEDURE setobtype('100');


--
-- Name: setobtype; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER setobtype
    BEFORE INSERT ON biosamplelist
    FOR EACH ROW
    EXECUTE PROCEDURE setobtype('102');


--
-- Name: setobtype; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER setobtype
    BEFORE INSERT ON pedigreelink
    FOR EACH ROW
    EXECUTE PROCEDURE setobtype('335');


--
-- Name: setobtype; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER setobtype
    BEFORE INSERT ON biosequenceob
    FOR EACH ROW
    EXECUTE PROCEDURE setobtype('115');


--
-- Name: setobtype; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER setobtype
    BEFORE INSERT ON biosequencefeaturefact
    FOR EACH ROW
    EXECUTE PROCEDURE setobtype('117');


--
-- Name: setobtype; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER setobtype
    BEFORE INSERT ON sequencingfunction
    FOR EACH ROW
    EXECUTE PROCEDURE setobtype('120');


--
-- Name: setobtype; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER setobtype
    BEFORE INSERT ON datasourceob
    FOR EACH ROW
    EXECUTE PROCEDURE setobtype('125');


--
-- Name: setobtype; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER setobtype
    BEFORE INSERT ON importprocedureob
    FOR EACH ROW
    EXECUTE PROCEDURE setobtype('130');


--
-- Name: setobtype; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER setobtype
    BEFORE INSERT ON importfunction
    FOR EACH ROW
    EXECUTE PROCEDURE setobtype('135');


--
-- Name: setobtype; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER setobtype
    BEFORE INSERT ON displayprocedureob
    FOR EACH ROW
    EXECUTE PROCEDURE setobtype('140');


--
-- Name: setobtype; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER setobtype
    BEFORE INSERT ON displayfunction
    FOR EACH ROW
    EXECUTE PROCEDURE setobtype('145');


--
-- Name: setobtype; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER setobtype
    BEFORE INSERT ON phenotypestudy
    FOR EACH ROW
    EXECUTE PROCEDURE setobtype('150');


--
-- Name: setobtype; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER setobtype
    BEFORE INSERT ON phenotypeobservation
    FOR EACH ROW
    EXECUTE PROCEDURE setobtype('155');


--
-- Name: setobtype; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER setobtype
    BEFORE INSERT ON geneticob
    FOR EACH ROW
    EXECUTE PROCEDURE setobtype('160');


--
-- Name: setobtype; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER setobtype
    BEFORE INSERT ON geneticoblist
    FOR EACH ROW
    EXECUTE PROCEDURE setobtype('165');


--
-- Name: setobtype; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER setobtype
    BEFORE INSERT ON geneticfunctionfact
    FOR EACH ROW
    EXECUTE PROCEDURE setobtype('190');


--
-- Name: setobtype; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER setobtype
    BEFORE INSERT ON geneticexpressionfact
    FOR EACH ROW
    EXECUTE PROCEDURE setobtype('195');


--
-- Name: setobtype; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER setobtype
    BEFORE INSERT ON geneticfact
    FOR EACH ROW
    EXECUTE PROCEDURE setobtype('200');


--
-- Name: setobtype; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER setobtype
    BEFORE INSERT ON geneproductlink
    FOR EACH ROW
    EXECUTE PROCEDURE setobtype('201');


--
-- Name: setobtype; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER setobtype
    BEFORE INSERT ON generegulationlink
    FOR EACH ROW
    EXECUTE PROCEDURE setobtype('202');


--
-- Name: setobtype; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER setobtype
    BEFORE INSERT ON genotypestudy
    FOR EACH ROW
    EXECUTE PROCEDURE setobtype('290');


--
-- Name: setobtype; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER setobtype
    BEFORE INSERT ON genetictestfact
    FOR EACH ROW
    EXECUTE PROCEDURE setobtype('305');


--
-- Name: setobtype; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER setobtype
    BEFORE INSERT ON genotypeobservation
    FOR EACH ROW
    EXECUTE PROCEDURE setobtype('300');


--
-- Name: setobtype; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER setobtype
    BEFORE INSERT ON geneticlocationfact
    FOR EACH ROW
    EXECUTE PROCEDURE setobtype('175');


--
-- Name: setobtype; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER setobtype
    BEFORE INSERT ON geneticlocationlist
    FOR EACH ROW
    EXECUTE PROCEDURE setobtype('180');


--
-- Name: setobtype; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER setobtype
    BEFORE INSERT ON workflowob
    FOR EACH ROW
    EXECUTE PROCEDURE setobtype('205');


--
-- Name: setobtype; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER setobtype
    BEFORE INSERT ON workflowstageob
    FOR EACH ROW
    EXECUTE PROCEDURE setobtype('210');


--
-- Name: setobtype; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER setobtype
    BEFORE INSERT ON workstagevisitfact
    FOR EACH ROW
    EXECUTE PROCEDURE setobtype('225');


--
-- Name: setobtype; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER setobtype
    BEFORE INSERT ON workflowmembershiplink
    FOR EACH ROW
    EXECUTE PROCEDURE setobtype('215');


--
-- Name: setobtype; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER setobtype
    BEFORE INSERT ON workflowlink
    FOR EACH ROW
    EXECUTE PROCEDURE setobtype('220');


--
-- Name: setobtype; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER setobtype
    BEFORE INSERT ON microarrayfact
    FOR EACH ROW
    EXECUTE PROCEDURE setobtype('230');


--
-- Name: setobtype; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER setobtype
    BEFORE INSERT ON microarrayspotfact
    FOR EACH ROW
    EXECUTE PROCEDURE setobtype('235');


--
-- Name: setobtype; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER setobtype
    BEFORE INSERT ON geneexpressionstudy
    FOR EACH ROW
    EXECUTE PROCEDURE setobtype('240');


--
-- Name: setobtype; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER setobtype
    BEFORE INSERT ON microarrayobservation
    FOR EACH ROW
    EXECUTE PROCEDURE setobtype('250');


--
-- Name: setobtype; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER setobtype
    BEFORE INSERT ON biodatabaseob
    FOR EACH ROW
    EXECUTE PROCEDURE setobtype('315');


--
-- Name: setobtype; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER setobtype
    BEFORE INSERT ON databasesearchstudy
    FOR EACH ROW
    EXECUTE PROCEDURE setobtype('320');


--
-- Name: setobtype; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER setobtype
    BEFORE INSERT ON databasesearchobservation
    FOR EACH ROW
    EXECUTE PROCEDURE setobtype('325');


--
-- Name: setobtype; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER setobtype
    BEFORE INSERT ON sequencealignmentfact
    FOR EACH ROW
    EXECUTE PROCEDURE setobtype('330');


--
-- Name: setobtype; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER setobtype
    BEFORE INSERT ON biosamplealiquotfact
    FOR EACH ROW
    EXECUTE PROCEDURE setobtype('400');


--
-- Name: setobtype; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER setobtype
    BEFORE INSERT ON securityprocedureob
    FOR EACH ROW
    EXECUTE PROCEDURE setobtype('460');


--
-- Name: setobtype; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER setobtype
    BEFORE INSERT ON securityfunction
    FOR EACH ROW
    EXECUTE PROCEDURE setobtype('465');


--
-- Name: setobtype; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER setobtype
    BEFORE INSERT ON biolibraryob
    FOR EACH ROW
    EXECUTE PROCEDURE setobtype('485');


--
-- Name: setobtype; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER setobtype
    BEFORE INSERT ON biolibraryconstructionfunction
    FOR EACH ROW
    EXECUTE PROCEDURE setobtype('495');


--
-- Name: setobtype; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER setobtype
    BEFORE INSERT ON librarysequencingfunction
    FOR EACH ROW
    EXECUTE PROCEDURE setobtype('500');


--
-- Name: setobtype; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER setobtype
    BEFORE INSERT ON analysisprocedureob
    FOR EACH ROW
    EXECUTE PROCEDURE setobtype('540');


--
-- Name: setobtype; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER setobtype
    BEFORE INSERT ON datasourcelist
    FOR EACH ROW
    EXECUTE PROCEDURE setobtype('550');


--
-- Name: setobtype; Type: TRIGGER; Schema: public; Owner: agrbrdf
--

CREATE TRIGGER setobtype
    BEFORE INSERT ON analysisfunction
    FOR EACH ROW
    EXECUTE PROCEDURE setobtype('545');


--
-- Name: $2; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY workstagevisitfact
    ADD CONSTRAINT "$2" FOREIGN KEY (workflowstage) REFERENCES workflowstageob(obid);


