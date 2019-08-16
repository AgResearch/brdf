--
-- Name: obid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY workflowob ALTER COLUMN obid SET DEFAULT nextval(('ob_obidseq'::text)::regclass);


--
-- Name: obtypeid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY workflowob ALTER COLUMN obtypeid SET DEFAULT 0;


--
-- Name: createddate; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY workflowob ALTER COLUMN createddate SET DEFAULT now();


--
-- Name: checkedout; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY workflowob ALTER COLUMN checkedout SET DEFAULT false;


--
-- Name: statuscode; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY workflowob ALTER COLUMN statuscode SET DEFAULT 1;


--
-- Name: workflowob_obid_key; Type: CONSTRAINT; Schema: public; Owner: agrbrdf; Tablespace: 
--

ALTER TABLE ONLY workflowob
    ADD CONSTRAINT workflowob_obid_key UNIQUE (obid);


