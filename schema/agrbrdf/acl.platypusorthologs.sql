--
-- Name: platypusorthologs; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE platypusorthologs FROM PUBLIC;
REVOKE ALL ON TABLE platypusorthologs FROM agrbrdf;
GRANT ALL ON TABLE platypusorthologs TO agrbrdf;
GRANT SELECT ON TABLE platypusorthologs TO gbs;


