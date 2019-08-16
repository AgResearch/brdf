--
-- Name: librarysequencingfact_librarysequencingfunction_fkey; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY librarysequencingfact
    ADD CONSTRAINT librarysequencingfact_librarysequencingfunction_fkey FOREIGN KEY (librarysequencingfunction) REFERENCES librarysequencingfunction(obid);


