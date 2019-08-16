--
-- Name: genotypestudyfact; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE genotypestudyfact FROM PUBLIC;
REVOKE ALL ON TABLE genotypestudyfact FROM agrbrdf;
GRANT ALL ON TABLE genotypestudyfact TO agrbrdf;
GRANT SELECT ON TABLE genotypestudyfact TO gbs;


