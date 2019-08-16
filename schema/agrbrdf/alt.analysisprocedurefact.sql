--
-- Name: analysisprocedurefact_analysisprocedureob_fkey; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY analysisprocedurefact
    ADD CONSTRAINT analysisprocedurefact_analysisprocedureob_fkey FOREIGN KEY (analysisprocedureob) REFERENCES analysisprocedureob(obid);


