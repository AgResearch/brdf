--
-- Name: obid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY geneticexpressionfact ALTER COLUMN obid SET DEFAULT nextval(('ob_obidseq'::text)::regclass);


--
-- Name: obtypeid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY geneticexpressionfact ALTER COLUMN obtypeid SET DEFAULT 0;


--
-- Name: createddate; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY geneticexpressionfact ALTER COLUMN createddate SET DEFAULT now();


--
-- Name: checkedout; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY geneticexpressionfact ALTER COLUMN checkedout SET DEFAULT false;


--
-- Name: statuscode; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY geneticexpressionfact ALTER COLUMN statuscode SET DEFAULT 1;


--
-- Name: geneticexpressionfact_obid_key; Type: CONSTRAINT; Schema: public; Owner: agrbrdf; Tablespace: 
--

ALTER TABLE ONLY geneticexpressionfact
    ADD CONSTRAINT geneticexpressionfact_obid_key UNIQUE (obid);


--
-- Name: $2; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY geneticexpressionfact
    ADD CONSTRAINT "$2" FOREIGN KEY (geneticob) REFERENCES geneticob(obid);


--
-- Name: $3; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY geneticexpressionfact
    ADD CONSTRAINT "$3" FOREIGN KEY (biosequenceob) REFERENCES biosequenceob(obid);


