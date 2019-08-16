--
-- Name: obid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY analysisfunction ALTER COLUMN obid SET DEFAULT nextval(('ob_obidseq'::text)::regclass);


--
-- Name: obtypeid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY analysisfunction ALTER COLUMN obtypeid SET DEFAULT 0;


--
-- Name: createddate; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY analysisfunction ALTER COLUMN createddate SET DEFAULT now();


--
-- Name: checkedout; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY analysisfunction ALTER COLUMN checkedout SET DEFAULT false;


--
-- Name: statuscode; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY analysisfunction ALTER COLUMN statuscode SET DEFAULT 1;


--
-- Name: analysisfunction_obid_key; Type: CONSTRAINT; Schema: public; Owner: agrbrdf; Tablespace: 
--

ALTER TABLE ONLY analysisfunction
    ADD CONSTRAINT analysisfunction_obid_key UNIQUE (obid);


--
-- Name: analysisfunction_analysisprocedureob_fkey; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY analysisfunction
    ADD CONSTRAINT analysisfunction_analysisprocedureob_fkey FOREIGN KEY (analysisprocedureob) REFERENCES analysisprocedureob(obid);


--
-- Name: analysisfunction_datasourcelist_fkey; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY analysisfunction
    ADD CONSTRAINT analysisfunction_datasourcelist_fkey FOREIGN KEY (datasourcelist) REFERENCES datasourcelist(obid);


--
-- Name: analysisfunction_datasourceob_fkey; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY analysisfunction
    ADD CONSTRAINT analysisfunction_datasourceob_fkey FOREIGN KEY (datasourceob) REFERENCES datasourceob(obid);


