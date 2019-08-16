--
-- Name: obid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY biolibraryconstructionfunction ALTER COLUMN obid SET DEFAULT nextval(('ob_obidseq'::text)::regclass);


--
-- Name: obtypeid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY biolibraryconstructionfunction ALTER COLUMN obtypeid SET DEFAULT 0;


--
-- Name: createddate; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY biolibraryconstructionfunction ALTER COLUMN createddate SET DEFAULT now();


--
-- Name: checkedout; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY biolibraryconstructionfunction ALTER COLUMN checkedout SET DEFAULT false;


--
-- Name: statuscode; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY biolibraryconstructionfunction ALTER COLUMN statuscode SET DEFAULT 1;


--
-- Name: biolibraryconstructionfunction_obid_key; Type: CONSTRAINT; Schema: public; Owner: agrbrdf; Tablespace: 
--

ALTER TABLE ONLY biolibraryconstructionfunction
    ADD CONSTRAINT biolibraryconstructionfunction_obid_key UNIQUE (obid);


--
-- Name: biolibraryconstructionfunction_biolibraryob_fkey; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY biolibraryconstructionfunction
    ADD CONSTRAINT biolibraryconstructionfunction_biolibraryob_fkey FOREIGN KEY (biolibraryob) REFERENCES biolibraryob(obid);


--
-- Name: biolibraryconstructionfunction_bioprotocolob_fkey; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY biolibraryconstructionfunction
    ADD CONSTRAINT biolibraryconstructionfunction_bioprotocolob_fkey FOREIGN KEY (bioprotocolob) REFERENCES bioprotocolob(obid);


--
-- Name: biolibraryconstructionfunction_biosampleob_fkey; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY biolibraryconstructionfunction
    ADD CONSTRAINT biolibraryconstructionfunction_biosampleob_fkey FOREIGN KEY (biosampleob) REFERENCES biosampleob(obid);


--
-- Name: biolibraryconstructionfunction_labresourcelist_fkey; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY biolibraryconstructionfunction
    ADD CONSTRAINT biolibraryconstructionfunction_labresourcelist_fkey FOREIGN KEY (labresourcelist) REFERENCES labresourcelist(obid);


--
-- Name: biolibraryconstructionfunction_labresourceob_fkey; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY biolibraryconstructionfunction
    ADD CONSTRAINT biolibraryconstructionfunction_labresourceob_fkey FOREIGN KEY (labresourceob) REFERENCES labresourceob(obid);


