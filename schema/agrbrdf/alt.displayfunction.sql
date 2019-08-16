--
-- Name: obid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY displayfunction ALTER COLUMN obid SET DEFAULT nextval(('ob_obidseq'::text)::regclass);


--
-- Name: obtypeid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY displayfunction ALTER COLUMN obtypeid SET DEFAULT 0;


--
-- Name: createddate; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY displayfunction ALTER COLUMN createddate SET DEFAULT now();


--
-- Name: checkedout; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY displayfunction ALTER COLUMN checkedout SET DEFAULT false;


--
-- Name: statuscode; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY displayfunction ALTER COLUMN statuscode SET DEFAULT 1;


--
-- Name: displayfunction_obid_key; Type: CONSTRAINT; Schema: public; Owner: agrbrdf; Tablespace: 
--

ALTER TABLE ONLY displayfunction
    ADD CONSTRAINT displayfunction_obid_key UNIQUE (obid);


--
-- Name: $2; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY displayfunction
    ADD CONSTRAINT "$2" FOREIGN KEY (datasourceob) REFERENCES datasourceob(obid);


--
-- Name: $3; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY displayfunction
    ADD CONSTRAINT "$3" FOREIGN KEY (displayprocedureob) REFERENCES displayprocedureob(obid);


