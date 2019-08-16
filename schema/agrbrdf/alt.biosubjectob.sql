--
-- Name: obid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY biosubjectob ALTER COLUMN obid SET DEFAULT nextval(('ob_obidseq'::text)::regclass);


--
-- Name: obtypeid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY biosubjectob ALTER COLUMN obtypeid SET DEFAULT 0;


--
-- Name: createddate; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY biosubjectob ALTER COLUMN createddate SET DEFAULT now();


--
-- Name: checkedout; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY biosubjectob ALTER COLUMN checkedout SET DEFAULT false;


--
-- Name: statuscode; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY biosubjectob ALTER COLUMN statuscode SET DEFAULT 1;


--
-- Name: biosubjectob_obid_key; Type: CONSTRAINT; Schema: public; Owner: agrbrdf; Tablespace: 
--

ALTER TABLE ONLY biosubjectob
    ADD CONSTRAINT biosubjectob_obid_key UNIQUE (obid);


