--
-- Name: obid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY phenotypeobservation ALTER COLUMN obid SET DEFAULT nextval(('ob_obidseq'::text)::regclass);


--
-- Name: obtypeid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY phenotypeobservation ALTER COLUMN obtypeid SET DEFAULT 0;


--
-- Name: createddate; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY phenotypeobservation ALTER COLUMN createddate SET DEFAULT now();


--
-- Name: checkedout; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY phenotypeobservation ALTER COLUMN checkedout SET DEFAULT false;


--
-- Name: statuscode; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY phenotypeobservation ALTER COLUMN statuscode SET DEFAULT 1;


--
-- Name: phenotypeobservation_obid_key; Type: CONSTRAINT; Schema: public; Owner: agrbrdf; Tablespace: 
--

ALTER TABLE ONLY phenotypeobservation
    ADD CONSTRAINT phenotypeobservation_obid_key UNIQUE (obid);


--
-- Name: $2; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY phenotypeobservation
    ADD CONSTRAINT "$2" FOREIGN KEY (biosampleob) REFERENCES biosampleob(obid);


--
-- Name: $3; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY phenotypeobservation
    ADD CONSTRAINT "$3" FOREIGN KEY (biosamplelist) REFERENCES biosamplelist(obid);


--
-- Name: $4; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY phenotypeobservation
    ADD CONSTRAINT "$4" FOREIGN KEY (biosubjectob) REFERENCES biosubjectob(obid);


--
-- Name: $5; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY phenotypeobservation
    ADD CONSTRAINT "$5" FOREIGN KEY (phenotypestudy) REFERENCES phenotypestudy(obid);


