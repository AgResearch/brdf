--
-- Name: obid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY biosequencefeaturefact ALTER COLUMN obid SET DEFAULT nextval(('ob_obidseq'::text)::regclass);


--
-- Name: obtypeid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY biosequencefeaturefact ALTER COLUMN obtypeid SET DEFAULT 0;


--
-- Name: createddate; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY biosequencefeaturefact ALTER COLUMN createddate SET DEFAULT now();


--
-- Name: checkedout; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY biosequencefeaturefact ALTER COLUMN checkedout SET DEFAULT false;


--
-- Name: statuscode; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY biosequencefeaturefact ALTER COLUMN statuscode SET DEFAULT 1;


--
-- Name: biosequencefeaturefact_obid_key; Type: CONSTRAINT; Schema: public; Owner: agrbrdf; Tablespace: 
--

ALTER TABLE ONLY biosequencefeaturefact
    ADD CONSTRAINT biosequencefeaturefact_obid_key UNIQUE (obid);


--
-- Name: $2; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY biosequencefeaturefact
    ADD CONSTRAINT "$2" FOREIGN KEY (biosequenceob) REFERENCES biosequenceob(obid);


