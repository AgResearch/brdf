--
-- Name: obid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY databasesearchobservation ALTER COLUMN obid SET DEFAULT nextval(('ob_obidseq'::text)::regclass);


--
-- Name: obtypeid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY databasesearchobservation ALTER COLUMN obtypeid SET DEFAULT 0;


--
-- Name: createddate; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY databasesearchobservation ALTER COLUMN createddate SET DEFAULT now();


--
-- Name: checkedout; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY databasesearchobservation ALTER COLUMN checkedout SET DEFAULT false;


--
-- Name: statuscode; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY databasesearchobservation ALTER COLUMN statuscode SET DEFAULT 1;


--
-- Name: databasesearchobservation_obid_key; Type: CONSTRAINT; Schema: public; Owner: agrbrdf; Tablespace: 
--

ALTER TABLE ONLY databasesearchobservation
    ADD CONSTRAINT databasesearchobservation_obid_key UNIQUE (obid);


--
-- Name: $2; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY databasesearchobservation
    ADD CONSTRAINT "$2" FOREIGN KEY (databasesearchstudy) REFERENCES databasesearchstudy(obid);


--
-- Name: $3; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY databasesearchobservation
    ADD CONSTRAINT "$3" FOREIGN KEY (querysequence) REFERENCES biosequenceob(obid);


--
-- Name: $4; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY databasesearchobservation
    ADD CONSTRAINT "$4" FOREIGN KEY (hitsequence) REFERENCES biosequenceob(obid);


